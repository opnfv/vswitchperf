function copyToClipboard(text){

	var dummy = document.createElement("textarea");
    document.body.appendChild(dummy);
    dummy.value = text;
    dummy.select();

	try{
	    var successful = document.execCommand('copy');
	    if(!successful)
	    	alert('Error copying to clipboard');
	}catch (err){
		alert('Error copying to clipboard');			   
	}
	document.body.removeChild(dummy);
}
