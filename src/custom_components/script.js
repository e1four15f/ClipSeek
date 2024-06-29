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
    window.setTimeout(() => {
      setFrameHeight(document.documentElement.clientHeight)
    }, 0)
  })

  // Optionally, if auto-height computation fails, you can manually set it
  // setFrameHeight(200)
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
function renderMedia(props) {
  const images = props.media;
  const n_cols = props.n_cols;
  const resources_url = props.resources_url

  // Clearing container and create columns
  var container = document.getElementById('container');
  container.innerHTML = '';

  var columns = Array.from({ length: n_cols }, () => {
    var column = document.createElement('div');
    column.className = 'column';
    container.appendChild(column);
    return column;
  });

  // Distribute images into columns
  images.forEach((image, index) => {
    var imgDiv = document.createElement('div');
    imgDiv.className = 'open-modal';
    imgDiv.setAttribute('index', index);
    imgDiv.setAttribute('data-content', image.dataContent);
    var img = document.createElement('img');
    img.src = resources_url + '/' + image.src;
    imgDiv.appendChild(img);
    columns[index % columns.length].appendChild(imgDiv);
  });

  // Create and append the modal
  const buttons = document.getElementsByClassName('open-modal');
  const modal = document.getElementById('modal');
  Array.from(buttons).forEach((button) => {
    button.onclick = function(event) {
      // Display element
      var modal = document.getElementById('modal');
      modal.style.display = 'block';

      // Update content
      var modalBody = document.getElementById('modal-body');
      var content = button.getAttribute('data-content');
      modalBody.textContent = content;

      // Move modal window to scroll position
      var modalWindow = document.getElementById('modal-window');
      var eventY = event.clientY;
      var viewportHeight = window.innerHeight;
      var percentY = (eventY / viewportHeight) * 100;
      modalWindow.style.top = percentY + '%';
      modalWindow.style.transform = 'translate(-50%, -50%)';
    };
  });

  const close = document.getElementById('modal-close');
  close.onclick = function() {
    modal.style.display = 'none';
  };

  window.onclick = function(event) {
    if (event.target == modal) {
      modal.style.display = 'none';
    }
  };
}


function logHandler(props) {
  console.log("Received from Streamlit: " + JSON.stringify(props))
}

// ----------------------------------------------------
// Finally, initialize component passing in pipeline
initialize(
  [
    logHandler,
    renderMedia,
  ]
)
