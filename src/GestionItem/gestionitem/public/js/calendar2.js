// Title: Tigra Calendar
// URL: http://www.softcomplex.com/products/tigra_calendar/
// Version: 3.2 (American date format)
// Date: 10/14/2002 (mm/dd/yyyy)
// Feedback: feedback@softcomplex.com (specify product title in the subject)
// Note: Permission given to use this script in ANY kind of applications if
//    header lines are left unchanged.
// Note: Script consists of two files: calendar?.js and calendar.html
// About us: Our company provides offshore IT consulting services.
//    Contact us at sales@softcomplex.com if you have any programming task you
//    want to be handled by professionals. Our typical hourly rate is $20.

// if two digit year input dates after this year considered 20 century.
var NUM_CENTYEAR = 30;
// is time input control required by default
var BUL_TIMECOMPONENT = false;
// are year scrolling buttons required by default
var BUL_YEARSCROLL = true;

var calendars = [];
var RE_NUM = /^\-?\d+$/;

function calendar2(obj_target) {

	// assing methods
	this.gen_date = cal_gen_date2;
	this.gen_time = cal_gen_time2;
	this.gen_tsmp = cal_gen_tsmp2;
	this.prs_date = cal_prs_date2;
	this.prs_time = cal_prs_time2;
	this.prs_tsmp = cal_prs_tsmp2;
	this.popup    = cal_popup2;

	// validate input parameters
	if (!obj_target)
		//return cal_error("Error calling the calendar: no target control specified");
		return cal_error("Error en la llamada al calendario: no se ha especificado el control target");
	if (obj_target.value == null)
		//return cal_error("Error calling the calendar: parameter specified is not valid tardet control");
		return cal_error("Error en la llamada al calendario: el parámetro especificado no es un control target válido");
	this.target = obj_target;
	this.time_comp = BUL_TIMECOMPONENT;
	this.year_scroll = BUL_YEARSCROLL;
	
	// register in global collections
	this.id = calendars.length;
	calendars[this.id] = this;
}

function cal_popup2 (str_datetime) {
	this.dt_current = this.prs_tsmp(str_datetime ? str_datetime : this.target.value);
	if (!this.dt_current) return;

	var obj_calwindow = window.open(
'../html/calendar.html?datetime=' + this.dt_current.valueOf()+ '&id=' + this.id,
		'Calendar', 'width=200,height='+(this.time_comp ? 215 : 190)+
		',status=no,resizable=no,top=200,left=200,dependent=yes,alwaysRaised=yes'
	);
	obj_calwindow.opener = window;
	obj_calwindow.focus();
}

// timestamp generating function
function cal_gen_tsmp2 (dt_datetime) {
	return(this.gen_date(dt_datetime) + ' ' + this.gen_time(dt_datetime));
}

// date generating function
function cal_gen_date2 (dt_datetime) {
	return ((dt_datetime.getDate() < 10 ? '0' : '') + dt_datetime.getDate() + "/" 
		+ (dt_datetime.getMonth() < 9 ? '0' : '') + (dt_datetime.getMonth() + 1) + "/"
		+ dt_datetime.getFullYear()
	);
}
// time generating function
function cal_gen_time2 (dt_datetime) {
	return (
		(dt_datetime.getHours() < 10 ? '0' : '') + dt_datetime.getHours() + ":"
		+ (dt_datetime.getMinutes() < 10 ? '0' : '') + (dt_datetime.getMinutes()) + ":"
		+ (dt_datetime.getSeconds() < 10 ? '0' : '') + (dt_datetime.getSeconds())
	);
}

// timestamp parsing function
function cal_prs_tsmp2 (str_datetime) {
	// if no parameter specified return current timestamp
	if (!str_datetime)
		return (new Date());

	// if positive integer treat as milliseconds from epoch
	if (RE_NUM.exec(str_datetime))
		return new Date(str_datetime);
		
	// else treat as date in string format
	var arr_datetime = str_datetime.split(' ');
	return this.prs_time(arr_datetime[1], this.prs_date(arr_datetime[0]));
}

// date parsing function
function cal_prs_date2 (str_date) {

	var arr_date = "";
	if(str_date.indexOf('/') != -1)
		arr_date = str_date.split('/');
	else 
		arr_date = str_date.split('-');

	if (arr_date.length != 3) 
		return alert ("Formato de fecha inválido: '" + str_date + "'.\nEl formato aceptado es dd-mm-yyyy.");
	if (!arr_date[0]) 
		return alert ("Formato de fecha inválido: '" + str_date + "'.\nNo se encuentra el día del mes.");
	if (!RE_NUM.exec(arr_date[0])) 
		return alert ("Día de Mes inválido: '" + arr_date[0] + "'.\nLos valores válidos son los enteros sin signo.");
	if (!arr_date[1]) 
		return alert ("Formato de fecha inválido: '" + str_date + "'.\nNo se encuentra el Mes.");
	if (!RE_NUM.exec(arr_date[1])) 
		return alert ("Mes inválido: '" + arr_date[1] + "'.\nLos valores válidos son los enteros sin signo.");
	if (!arr_date[2]) 
		return alert ("Formato de fecha inválido: '" + str_date + "'.\nNo se encuentra el año.");
	if (!RE_NUM.exec(arr_date[2])) 
		//return alert ("Invalid year value: '" + arr_date[2] + "'.\nAllowed values are unsigned integers.");
		return alert ("Año inválido: '" + arr_date[2] + "'.\nLos valores válidos son los enteros sin signo.");

	var dt_date = new Date();
	dt_date.setDate(1);

	if (arr_date[1] < 1 || arr_date[1] > 12) return call_error ("Mes inválido: '" + arr_date[1] + "'.\nEl rango permitido es 01-12.");
	dt_date.setMonth(arr_date[1]-1);
	 
	if (arr_date[2] < 100) arr_date[2] = Number(arr_date[2]) + (arr_date[2] < NUM_CENTYEAR ? 2000 : 1900);
	dt_date.setFullYear(arr_date[2]);

	var dt_numdays = new Date(arr_date[2], arr_date[1], 0);
	dt_date.setDate(arr_date[0]);
	if (dt_date.getMonth() != (arr_date[1]-1)) return alert ("Día de mes inválido: '" + arr_date[0] + "'.\nEl rango permitido es 01-"+dt_numdays.getDate()+".");

	return (dt_date)
}

// time parsing function
function cal_prs_time2 (str_time, dt_date) {

	if (!dt_date) return null;
	var arr_time = String(str_time ? str_time : '').split(':');

	if (!arr_time[0]) dt_date.setHours(0);
	else if (RE_NUM.exec(arr_time[0])) 
		if (arr_time[0] < 24) dt_date.setHours(arr_time[0]);
		else return cal_error ("Hora inválida: '" + arr_time[0] + "'.\nEl rango permitido es 00-23.");
	else return cal_error ("Hora inválida: '" + arr_time[0] + "'.\nLos valores permitidos son los enteros sin signo.");
	
	if (!arr_time[1]) dt_date.setMinutes(0);
	else if (RE_NUM.exec(arr_time[1]))
		if (arr_time[1] < 60) dt_date.setMinutes(arr_time[1]);
		else return cal_error ("Minutos inválidos: '" + arr_time[1] + "'.\nEl rango permitido es 00-59.");
	else return cal_error ("Minutos inválidos: '" + arr_time[1] + "'.\nLos valores permitidos son los enteros sin signo.");

	if (!arr_time[2]) dt_date.setSeconds(0);
	else if (RE_NUM.exec(arr_time[2]))
		if (arr_time[2] < 60) dt_date.setSeconds(arr_time[2]);
		else return cal_error ("Segundo inválido: '" + arr_time[2] + "'.\nEl rango permitido es 00-59.");
	else return cal_error ("Segundo inválido: '" + arr_time[2] + "'.\nLos valores permitidos son los enteros sin signo.");

	dt_date.setMilliseconds(0);
	return dt_date;
}

function cal_error (str_message) {
	alert (str_message);
	return null;
}

