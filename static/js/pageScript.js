	function startTime() {
		
		var list = document.getElementsByTagName("img");
		
		var i=1;
		while(!(i>list.length)){
			var id1 = "header_"+i;
			var id2 = "img_"+i;
			var id3 = "in_"+i;
			
			var val = document.getElementById(id3).value;
			
			requestForRate(id1,val,id2);
			i++;
		}
  	    
  	    var t = setTimeout(function(){startTime()},5000);
  	}
	
	function requestForRate(id1,streamId,id2){
		
		var context = document.getElementById("context").value;
		var greenLink = context+"/resources/assets/img/green.png";
		var yellowLink = context+"/resources/assets/img/yellow.png";
		var redLink = context+"/resources/assets/img/red.png";
		
	        var xmlhttp = new XMLHttpRequest();
	        xmlhttp.onreadystatechange = function() {
	        	    var str = xmlhttp.responseText;
	        	    var f = str.indexOf("_")+1;
	        	    var l = str.indexOf(",");
	        	    var x = str.substring(f,l);
	                document.getElementById(id1).innerHTML = "&nbsp;&nbsp;"+x;
	                
	                if(x<=20){
	    				document.getElementById(id2).setAttribute("src",greenLink);
	    			}else if(x>20 && x<=35){
	    				document.getElementById(id2).setAttribute("src",yellowLink);
	    			}
	    			else{
	    				document.getElementById(id2).setAttribute("src",redLink);
	    			}
	            
	        }
	        xmlhttp.open("GET", "/transfer-ui/PageController/rateRequest?id=" + streamId, true);
	        xmlhttp.send();
	}
	
	function deletePage(id) {

		window.location = $("#context").val()+"/PageController/delete?id=" + id;
	}
	function habu(id){
		document.getElementById("deleteId").value = id;
	}
	function show(id){
		
		var key = id.split("_");
		var deleteKey = "delete_"+key[1];
		var editKey = "edit_"+key[1];
		var link = $("#context").val()+"/PageController/form?id=" + key[1];	
		var val = document.getElementById(id).value;
		if(val=="on"){
			
			document.getElementById(id).value = "off";
			document.getElementById(deleteKey).disabled = true;
			document.getElementById(editKey).removeAttribute("data-target");
			document.getElementById(editKey).removeAttribute("href");
			document.getElementById(editKey).setAttribute("href","#");
			document.getElementById(editKey).style.opacity = "0.5";
			document.getElementById(editKey).style.filter  = 'alpha(opacity=50)'; //for IE
		}else{
			document.getElementById(id).value = "on";
			document.getElementById(deleteKey).disabled = false;
			document.getElementById(editKey).setAttribute("data-target","#editModal");
			document.getElementById(editKey).setAttribute("href",link);
			document.getElementById(editKey).style.opacity = "1";
			document.getElementById(editKey).style.filter  = 'alpha(opacity=100)'; //for IE
		}
		
		var list = document.getElementsByTagName("input");
		var i=0;
		while(i != list.length){
			if(list[i].value == "off"){
				document.getElementById("deleteAll").disabled = true;
				document.getElementById("startAll").disabled = true;
				document.getElementById("restartAll").disabled = true;
				document.getElementById("stopAll").disabled = true;
				return;
			}else{
				document.getElementById("deleteAll").disabled = false;
				document.getElementById("startAll").disabled = false;
				document.getElementById("restartAll").disabled = false;
				document.getElementById("stopAll").disabled = false;
			}
			i++;
		}
			
	}