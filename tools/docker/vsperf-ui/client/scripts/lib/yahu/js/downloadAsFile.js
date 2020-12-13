/**
 * This function creates a Json file to support client-side file download
 */

function downloadAsFile(filename, text, mimeType='text/plain') {
    var data = new Blob([text], {type: mimeType});
    var url = window.URL.createObjectURL(data);

    var dummy = document.createElement('a');
  	dummy.setAttribute('href', url);
  	dummy.setAttribute('download', filename);

  	dummy.style.display = 'none';
  	document.body.appendChild(dummy);
  	dummy.click();
  	document.body.removeChild(dummy);
}
