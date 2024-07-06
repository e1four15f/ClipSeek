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
  const medias = props.media;
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

  // Distribute media into columns
  medias.forEach((media, index) => {
    var mediaDiv = document.createElement('div');
    mediaDiv.className = 'open-modal';
    mediaDiv.setAttribute('index', index);
    mediaDiv.mediaData = media;

    var mediaType = _detectMediaType(media.src);
    var mediaElement;
    if (mediaType === 'image') {
      mediaElement = document.createElement('img');
    } else if (mediaType === 'audio') {
      mediaElement = document.createElement('audio');
    } else if (mediaType === 'video') {
      mediaElement = document.createElement('video');
    } else {
      mediaElement = document.createElement('p');
      mediaElement.innerHTML = 'X'; // Display an X for unknown media types
    }
    mediaElement.src = resources_url + '/' + media.src;

    // Add visible info: Score
    var infoDiv = document.createElement('div');
    infoDiv.className = 'info';
    infoDiv.innerText = Number((media.dataContent.Score).toFixed(4));

    mediaDiv.appendChild(mediaElement);
    mediaDiv.appendChild(infoDiv);
    columns[index % columns.length].appendChild(mediaDiv);
  });

  // Create and append the modal
  const buttons = document.getElementsByClassName('open-modal');
  const modal = document.getElementById('modal');
  Array.from(buttons).forEach((button) => {
    button.onclick = function(event) {
      // Display element
      var modal = document.getElementById('modal');
      modal.style.display = 'block';

      // Retrieve media data
      var media = button.mediaData;

      // Update header
      var modalHeader = document.getElementById('modal-header').getElementsByTagName('h2')[0];
      modalHeader.textContent = `Filename: ${media.src.split('/').pop()}`;

      // Update body
      var modalBody = document.getElementById('modal-body');
      modalBody.innerHTML = '';

      var mediaType = _detectMediaType(media.src);
      var mediaElement;
      if (mediaType === 'image') {
        mediaElement = document.createElement('img');
      } else if (mediaType === 'audio') {
        mediaElement = document.createElement('audio');
        mediaElement.controls = true;
      } else if (mediaType === 'video') {
        mediaElement = document.createElement('video');
        mediaElement.controls = true;
      } else {
        mediaElement = document.createElement('p');
        mediaElement.innerHTML = 'X'; // Display an X for unknown media types
      }
      mediaElement.src = resources_url + '/' + media.src;
      modalBody.appendChild(mediaElement);

      var infoDiv = document.createElement('div');
      infoDiv.className = 'info';
      infoDiv.innerHTML = `
        <p>Score: ${media.dataContent.Score.toFixed(4)}</p>
        <p>Type: ${mediaType}</p>
        <p>Filename: ${media.src.split('/').pop()}</p>
      `;
      modalBody.appendChild(infoDiv);

      // Move modal window to scroll position
      var modalWindow = document.getElementById('modal-window');
      var eventY = event.clientY;

      modalWindow.style.top = eventY + 'px';
      modalWindow.style.left = '50%';
      modalWindow.style.transform = 'translateX(-50%)';
    };
  });

  const close = document.getElementById('modal-close');
  close.onclick = function() {
    modal.style.display = 'none';
    document.getElementById('modal-body').innerHTML = '';
  };

  window.onclick = function(event) {
    if (event.target == modal) {
      modal.style.display = 'none';
      document.getElementById('modal-body').innerHTML = '';
    }
  };
}

function _detectMediaType(url) {
  const extension = url.split('.').pop().toLowerCase().split('?')[0].split('#')[0];
  if (['jpg', 'jpeg', 'png', 'gif'].includes(extension)) {
    return 'image';
  } else if (['mp3', 'wav', 'ogg'].includes(extension)) {
    return 'audio';
  } else if (['mp4', 'avi', 'mov', 'wmv'].includes(extension)) {
    return 'video';
  } else {
    return 'unknown';
  }
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
