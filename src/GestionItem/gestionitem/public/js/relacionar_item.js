function verificar()
{
	if(document.formulario.fases.checked==true)
	{
		return true;
	}
              
              for(i=0; ele=document.formulario.fases[i]; i++){
    				if (ele.checked==true){
    					
    					return true;
    					
    				}
    				}
    				
    			
						 alert("Debe seleccionar al menos una fase");
    					 return false;
    					
    				
}
function mostrar(param) {
 
  obj = document.getElementById('ListaTodos');

  if (param)
  {
  	obj.style.display = (obj.style.display=='none') ? 'block' : 'none';
  }
}
boton=""
function valida(F) {
		
		if (boton=="Relacion")
		{  
   				for(j=0; ele=document.formulario.itemselect[j]; j++){ 
              		
    				if (ele.checked==true){
    					document.formulario.action="/item/saveRelacion/${item.id}"
        				F.filtros.value="Lista"
    					return true;
    					
    				}
    				}
    				
    			if(document.formulario.itemselect.checked==true){
			  		document.formulario.action="/item/saveRelacion/${item.id}"
			  		F.filtros.value=""
			  		return true;	
				}
    			alert("Debe seleccionar al menos un item para relacionar");
    			return false;
       	}
       	if (boton=="RelacionPH")
		{  
   				for(j=0; ele=document.formulario.itemselect[j]; j++){ 
              		
    				if (ele.checked==true){
    					document.formulario.action="/item/saveRelacion/${item.id}"
        				F.filtros.value="Lista"
    					return true;
    					
    				}
    				}
    				
    			if(document.formulario.itemselect.checked==true){
			  		document.formulario.action="/item/saveRelacion/${item.id}"
			  		F.filtros.value="Lista"
			  		return true;	
				}
    			document.formulario.action="/item/relacionar_item/${item.id}/${fase.id}/1"
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
function verificarItems()
{	
			  
			  
              for(j=0; ele=document.formulario2.itemselect[j]; j++){ 
              		
    				if (ele.checked==true){
    					
    					return true;
    					
    				}
    				}
    				
    			if(document.formulario2.itemselect.checked==true)
			  		return true;	
	
    					 alert("Debe seleccionar al menos un item");
    					 return false;
    					
    				
}
        
