boton=""
function valida(F) {
		
		if (boton=="genlb")
		{  
   				for(j=0; ele=document.form1.itemselect[j]; j++){ 
              		
    				if (ele.checked==true){
    					document.form1.action="/item/guardar_linea_base/${fase.id}"
        				//F.filtros.value="Lista"
    					return true;	
    				}
    			}
    				
    			if(document.form1.itemselect.checked==true){
			  		document.form1.action="/item/guardar_linea_base/${fase.id}"
			  		//F.filtros.value=""
			  		return true;	
				}
    			alert("Debe seleccionar al menos un item para relacionar");
    			return false;
       	}
       	if (boton=="RelacionPH")
		{  
   				for(j=0; ele=document.form1.itemselect[j]; j++){ 
              		
    				if (ele.checked==true){
    					document.form1.action="/item/saveRelacion/${item.id}"
        				F.filtros.value="Lista"
    					return true;
    					
    				}
    				}
    				
    			if(document.form1.itemselect.checked==true){
			  		document.form1.action="/item/saveRelacion/${item.id}"
			  		F.filtros.value="Lista"
			  		return true;	
				}
    			document.form1.action="/item/relacionar_item/${item.id}/${fase.id}/1"
			  	F.filtros.value=""
       	}
       	
       	
       	
       	if(boton=="Buscar"){
        		if(F.filtros.value != "") {   
                	return true 
        		}
        		else if (F.filtros.value == ""){
        			return false
        		}	 
        }else if (boton=="ListarTodos"){
       	 	F.filtros.value=""
        		return true
        }				
}

function botonPresionado(botonP){
	boton=botonP
}  

        
