var modal = document.getElementById('demo-modal');
var modalBodyContent = document.getElementById('modal-body-content');
var buttons = document.getElementsByClassName('open-modal');
var close = modal.getElementsByClassName('close')[0];

Array.from(buttons).forEach(function(button) {
button.onclick = function() {
      var content = button.getAttribute('data-content');
      modalBodyContent.textContent = content;
      modal.style.display = 'block';
    };
});

close.onclick = function() {
    modal.style.display = 'none';
};

window.onclick = function(event) {
    if (event.target == modal) {
      modal.style.display = 'none';
    }
};

// ----------------------------------------------------
// Use these functions as is to perform required Streamlit
// component lifecycle actions:
//
// 1. Signal Streamlit client that component is ready
// 2. Signal Streamlit client to set visible height of the component
//    (this is optional, in case Streamlit doesn't correctly auto-set it)
// 3. Pass values from component to Streamlit client
//

// Helper function to send type and data messages to Streamlit client

const SET_COMPONENT_VALUE = "streamlit:setComponentValue"
const RENDER = "streamlit:render"
const COMPONENT_READY = "streamlit:componentReady"
const SET_FRAME_HEIGHT = "streamlit:setFrameHeight"

function _sendMessage(type, data) {
// copy data into object
var outboundData = Object.assign({
  isStreamlitMessage: true,
  type: type,
}, data)

if (type == SET_COMPONENT_VALUE) {
  console.log("_sendMessage data: " + JSON.stringify(data))
  console.log("_sendMessage outboundData: " + JSON.stringify(outboundData))
}

window.parent.postMessage(outboundData, "*")
}

function initialize(pipeline) {

// Hook Streamlit's message events into a simple dispatcher of pipeline handlers
window.addEventListener("message", (event) => {
  if (event.data.type == RENDER) {
    // The event.data.args dict holds any JSON-serializable value
    // sent from the Streamlit client. It is already deserialized.
    pipeline.forEach(handler => {
      handler(event.data.args)
    })
  }
})

_sendMessage(COMPONENT_READY, { apiVersion: 1 });

// Component should be mounted by Streamlit in an iframe, so try to autoset the iframe height.
window.addEventListener("load", () => {
  window.setTimeout(function () {
    setFrameHeight(document.documentElement.clientHeight)
  }, 0)
})

// Optionally, if auto-height computation fails, you can manually set it
// (uncomment below)
//setFrameHeight(200)
}

function setFrameHeight(height) {
_sendMessage(SET_FRAME_HEIGHT, { height: height })
}

// The `data` argument can be any JSON-serializable value.
function notifyHost(data) {
_sendMessage(SET_COMPONENT_VALUE, data)
}

// ----------------------------------------------------
// Your custom functionality for the component goes here:

function toggle(button, group) {
buttons = document.getElementsByClassName(group)
console.log(buttons)
for (let i = 0; i < buttons.length; i++) {
  console.log(buttons.item(i))
}

for (let i = 0; i < buttons.length; i++) {
  if (button.id == String(i) & button.className.includes("off")) {
    button.className = group + " on"
  } else if (button.id == String(i) & button.className.includes("on")) {
    button.className = group + " off"
  } else {
    buttons.item(i).className = group + " off"
  }
}

buttons = document.getElementsByClassName(group)
actions = []
for (let i = 0; i < buttons.length; i++) {
  btn = buttons.item(i)
  actions.push({ "action": btn.value, "value": btn.className.includes("on") })
}

states = {}
states['choice'] = {
  "name": group,
  "state": {
    "action": button.value,
    "value": button.className.includes("on")
  }
}
states["options"] = { "name": group, "states": actions }

notifyHost({
  value: states,
  dataType: "json",
})
}

// ----------------------------------------------------
// Here you can customize a pipeline of handlers for
// inbound properties from the Streamlit client app

// Set initial value sent from Streamlit!
function initializeProps_Handler(props) {
let header1 = document.getElementById("group_1_header")

let header2 = document.getElementById("group_2_header")
}
// Access values sent from Streamlit!
function dataUpdate_Handler(props) {
let msgLabel = document.getElementById("message_label")
}
// Simply log received data dictionary
function log_Handler(props) {
console.log("Received from Streamlit: " + JSON.stringify(props))
}

let pipeline = [initializeProps_Handler, dataUpdate_Handler, log_Handler]

// ----------------------------------------------------
// Finally, initialize component passing in pipeline

initialize(pipeline)
