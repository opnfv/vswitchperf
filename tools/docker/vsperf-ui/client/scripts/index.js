

function getRadioValue(name){
  radio = document.getElementsByName(name);
  for(i=0; i< radio.length; i++)
    if(radio[i].checked)
      return radio[i].value;
}