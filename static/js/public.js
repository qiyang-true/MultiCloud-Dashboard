String.prototype.ChinaLength = function(){
	return this.replace(/[^\x00-\xff]/g,"xx").length;
}
//写入cookies
function setCookie(name,value){
	var Days = 1;
	var exp = new Date(); 
	exp.setTime(exp.getTime() + Days*24*60*60*1000); 
	document.cookie = name + "="+ escape (value) + ";expires=" + exp.toGMTString() + ";path=/";
}
//读取cookies
function getCookie(name){
    var arr,reg=new RegExp("(^| )"+name+"=([^;]*)(;|$)");
    if(arr=document.cookie.match(reg))
        return unescape(arr[2]); 
    else 
        return null;
}
//删除cookies
function delCookie(name){
    var exp = new Date(); 
    exp.setTime(exp.getTime() - 1); 
    var cval=getCookie(name); 
    if(cval!=null) 
        document.cookie= name + "="+cval+";expires="+exp.toGMTString() + ";path=/";
}
// 数组去重
function unique(arr) {
    var result = [], hash = {};
    for (var i = 0, elem; (elem = arr[i]) != null; i++) {
        if (!hash[elem]) {
            result.push(elem);
            hash[elem] = true;
        }
    }
    return result;
}
/**
 * 上传图片预览
 * @param fileObj	上传文件表单对象
 * @param imgObj	要显示图片的对象
 */
function getFullPath(fileObj,imgObj){
	if(fileObj){
		//window.navigator.userAgent.indexOf("Firefox") 判断浏览器类型
		if (window.navigator.userAgent.indexOf("MSIE") >= 1) {
			fileObj.select();
			imgObj.style.filter = "progid:DXImageTransform.Microsoft.AlphaImageLoader(sizingMethod=scale);";
			imgObj.filters.item("DXImageTransform.Microsoft.AlphaImageLoader").src = document.selection.createRange().text;
			return;
		}else{
			if (fileObj.files) {
				imgObj.src = window.URL.createObjectURL(fileObj.files.item(0));return;
			}
			imgObj.src = fileObj.value;return;
		}
		imgObj.src = fileObj.value; return;
	}
}
/**
 * 双击修改
 * @param o object    this对象
 * @param url string  修改调用的url，格式为： 模块/控制器/方法  例:__MODULE__/flink/set_field
 * @param msg string  修改后的提示信息
 * 
 * 前台使用示例: ondblclick="doubleClickUpdate(this,'__MODULE__/article/set_field')"
 * 旧的改新的后台需要改这几处，post改为get，val改为value
 */
function doubleClickUpdate(o,url,msg){
	if(o.children.length >= 1){return false;}
	var id = o.id;
	var field = o.getAttribute('field');
	var con = o.innerHTML;
	var w = o.offsetWidth-3;
	var h = o.offsetHeight-5;
	o.innerHTML = "<input id='"+id+field+"' value='"+con+"' style='width:"+w+"px;height:"+h+"px;border:0px solid #fff;outline:0;'>";
	
	var update_input = document.getElementById(id+field);
	update_input.focus();
	update_input.onblur = function (){
		var val = update_input.value;
		if(typeof msg == 'undefined'){
			this.parentNode.innerHTML = val;
		}else{
			this.parentNode.innerHTML = msg;
		}
		//如果新旧值相同则不作为
		if(con == val){return;}
		var ajax;
		if(window.XMLHttpRequest){
			ajax = new XMLHttpRequest();
		}else{
			ajax = new ActiveXObject('Microsoft.XMLHTTP');
		}
		ajax.open('GET',url+'/id/'+id+'/field/'+field+'/value/'+val,true);
		ajax.send();
	}
}
/**
 * 弹窗
 * 
 * 获取弹窗内穿出的数据：
 *     在弹窗页面调用父级页面的方法，例:parent.xxx(data);
 * 在 xxx()方法中将获取到的数据赋值给 abc 变量；在的点击弹
 * 窗确定按钮后调用 yyy()方法，将 abc 变量的值填充到页面的
 * 某处。
 * 
 * @param idName String 弹窗ID,不可重复
 * @param src String    要打开窗口的url
 * @param func function 回调函数,点击确定按钮后执行
 * @param title String  弹窗标题
 * @param divW int      弹窗宽度
 * @param divH int      弹窗高度
 * @param bottun boolean  是否显示确定按钮
 * @param topSize int   position的top值，距离顶部的距离，可用百分比
 * @param leftSize int  position的left值，距离顶部的距离，可用百分比
 * 
 * 可选参数可以填 null
 * function popup(idName,src[,func][,title][,divW][,divH][,bottun][,topSize][,leftSize]);
 */
function popup(idName,src,func,title,divW,divH,bottun,topSize,leftSize){

	if(typeof idName == 'undefined'){alert('ID名称没有');return;}
	if(typeof src == 'undefined'){alert('src没有');return;}
	if(typeof title == 'undefined'){title = '这是标题';}
	if(typeof func != 'function'){func = function(){}	}
	
	//弹窗宽度和高度
	var divW = (typeof divW == 'number') ? divW : 700;
	var divH = (typeof divH == 'number') ? divH : 500;
	//底边栏高度
	var divBottomH = (bottun == true) ? 40 : 30;
	var topSize = (typeof topSize == 'number' || typeof topSize == 'string' ) ? topSize : '3%';
	var leftSize = (typeof leftSize == 'number' || typeof leftSize == 'string' ) ? leftSize : '15%';
	
	var divTopH = 30;		//标题高度
	var divMiddleH = divH - divTopH - divBottomH;//iframe高度
	
	var div			= document.createElement('div');
	var divTop		= document.createElement('div');
	var divBigSmall	= document.createElement('div');
	var divClose		= document.createElement('div');
	var divLittle		= document.createElement('div');
	var divMiddle	= document.createElement('div');
	var divBottom		= document.createElement('div');
	var divBottonOk		= document.createElement('div');
	var divBottonCancel	= document.createElement('div');
	var divWiden		= document.createElement('div');
	
	//div 样式
	div.style.cssText = "width:"+divW+"px;height:"+divH+"px;position:fixed;top:"+topSize+";left:"+leftSize+";z-index:999;display:block;font-size:16px;font-family:Arial,'Microsoft YaHei';font-weight:bold;border:1px solid #3377bb;overflow:hidden;";
	div.id = idName;
	div.innerHTML = '';
	
	//divTop 样式
	divTop.style.cssText = "width:100%;height:"+divTopH+"px;line-height:"+divTopH+"px;text-indent:20px;color:#fff;background:#5599dd;cursor:move;";
	divLittle.style.cssText = "width:15px;height:13px;float:right;margin:8px 12px 0 0;cursor:pointer;border: 1px solid #fff;line-height:11px;text-indent:5px;font-weight:normal;";
	divBigSmall.style.cssText = "width:15px;height:13px;float:right;margin:8px 10px 0 0;cursor:pointer;border: 1px solid #fff;";
	divClose.style.cssText = "width:15px;height:13px;float:right;margin:8px 12px 0 0;cursor:pointer;border: 1px solid #fff;line-height:10px;text-indent:4px;font-weight:normal;font-size:13px;";
	divTop.innerHTML = title;
	divLittle.innerHTML = '-';
	divClose.innerHTML = 'x';
	//divMiddle 样式
	divMiddle.style.cssText = "width:100%;background:#fafaff;height:"+divMiddleH+"px;";
	divMiddle.innerHTML = '<iframe src="'+src+'" id="popup'+idName+'" name="popup'+idName+'" frameborder="0" width="100%" height="100%"></iframe>';
	
	//divBottom 样式
	divBottom.style.cssText = "width:100%;height:"+divBottomH+"px;background:#fafaff;";
	//ok cancel 样式
	var bottonH = 25;
	divBottonOk.style.cssText = "width:60px;height:"+bottonH+"px;float:right;line-height:"+bottonH+"px;background:#3377bb;cursor:pointer;text-align:center;color:white;margin:8px 20px 0 0;";
	divBottonCancel.style.cssText = "width:60px;height:"+bottonH+"px;float:right;line-height:"+bottonH+"px;background:#3377bb;cursor:pointer;text-align:center;color:white;margin:8px 20px 0 0;";
	divBottonOk.innerHTML = '确定';
	divBottonCancel.innerHTML = '取消';
	//右下拉动窗口 样式
	divWiden.style.cssText = "width:10px;height:10px;position:absolute;bottom:0px;right:0px;cursor:se-resize;";
	//OK 事件
	divBottonOk.onclick = function (){
		func();
		document.body.removeChild(div);
	}
	//cancel 事件
	divClose.onclick = divBottonCancel.onclick = function (){
		document.body.removeChild(div);
	}
	//移动窗口事件
	var L = null;	//上一次移动div后的div.style.left的值
	var T = null;
	divTop.onmousedown = function(e){
		var e = e || event;
		var left = e.clientX - div.offsetLeft;
		var top = e.clientY - div.offsetTop;
		document.onmousemove = function (ev){
			var ev = ev || event;
			L = div.style.left = ev.clientX - left + 'px';
			T = div.style.top = ev.clientY - top + 'px';
		}
		document.onmouseup = function (){
			document.onmousemove = null;
			document.onmouseup = null;
		}
	}
	//窗口放大缩小
	divBigSmall.onclick = divTop.ondblclick = function (){
		if(document.body.offsetWidth != div.offsetWidth - 2){
			div.style.top = '0px';
			div.style.left = '0px';
			div.style.width = '100%';
			div.style.height = '100%';
			divMiddle.style.height = div.offsetHeight - divTopH - divBottomH - 2 +'px';
		}else{
			if(L && T){
				div.style.top = T;
				div.style.left = L;
			}else{
				div.style.top = '5%';
				div.style.left = '15%';
			}
			div.style.width = divW+'px';
			div.style.height = divH+'px';
			divMiddle.style.height = divMiddleH+'px';
		}
	}
	//拉动改变窗口大小
	var W = null;
	var H = null;
	divWiden.onmousedown = function (e){
		var e = e || event;
		var X = e.clientX;
		var Y = e.clientY;
		divW = div.offsetWidth;
		divH = div.offsetHeight;
		document.onmousemove = function (ev){
			var ev = ev || event;
			W = ev.clientX - X;
			H = ev.clientY - Y;
			div.style.width = divW + W +'px';
			div.style.height = divH + H +'px';
			divMiddleH = div.offsetHeight - divTopH - divBottomH - 2;
			divMiddle.style.height = divMiddleH+'px';
		}
		document.onmouseup = function (){
			document.onmousemove = null;
			document.onmouseup = null;
			divW = divW + W;
			divH = divH + H;
		}
	}
	//最小化
	divLittle.onclick = function (){
		if(div.offsetWidth != 202 && div.offsetHeight != divTopH+2){
			div.style.width = '200px';
			div.style.height = divTopH+'px';
		}else{
			div.style.width = divW+'px';
			div.style.height = divH+'px';
		}
	}
	div.appendChild(divTop);
	divTop.appendChild(divClose);
	divTop.appendChild(divBigSmall);
	divTop.appendChild(divLittle);
	div.appendChild(divMiddle);
	divBottom.appendChild(divWiden);
	if(bottun){
		divBottom.appendChild(divBottonCancel);
		divBottom.appendChild(divBottonOk);
	}
	div.appendChild(divBottom);
	
	if(!document.getElementById(idName)){
		document.body.appendChild(div);
	}
};