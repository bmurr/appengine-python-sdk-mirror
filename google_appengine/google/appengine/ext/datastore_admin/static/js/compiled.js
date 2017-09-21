var k,l=this,m=function(a){return"string"==typeof a},n=function(){},p=function(a){var b=typeof a;if("object"==b)if(a){if(a instanceof Array)return"array";if(a instanceof Object)return b;var d=Object.prototype.toString.call(a);if("[object Window]"==d)return"object";if("[object Array]"==d||"number"==typeof a.length&&"undefined"!=typeof a.splice&&"undefined"!=typeof a.propertyIsEnumerable&&!a.propertyIsEnumerable("splice"))return"array";if("[object Function]"==d||"undefined"!=typeof a.call&&"undefined"!=
typeof a.propertyIsEnumerable&&!a.propertyIsEnumerable("call"))return"function"}else return"null";else if("function"==b&&"undefined"==typeof a.call)return"object";return b},aa=function(a){var b=p(a);return"array"==b||"object"==b&&"number"==typeof a.length},q=function(a){var b=typeof a;return"object"==b&&null!=a||"function"==b},r=function(a,b){function d(){}d.prototype=b.prototype;a.C=b.prototype;a.prototype=new d;a.F=function(a,d,f){for(var c=Array(arguments.length-2),e=2;e<arguments.length;e++)c[e-
2]=arguments[e];return b.prototype[d].apply(a,c)}};var t=function(a){if(Error.captureStackTrace)Error.captureStackTrace(this,t);else{var b=Error().stack;b&&(this.stack=b)}a&&(this.message=String(a))};r(t,Error);t.prototype.name="CustomError";var ba=function(a,b){for(var d=a.split("%s"),c="",e=Array.prototype.slice.call(arguments,1);e.length&&1<d.length;)c+=d.shift()+e.shift();return c+d.join("%s")},u=String.prototype.trim?function(a){return a.trim()}:function(a){return a.replace(/^[\s\xa0]+|[\s\xa0]+$/g,"")},ja=function(a,b){if(b)a=a.replace(v,"&amp;").replace(ca,"&lt;").replace(da,"&gt;").replace(ea,"&quot;").replace(fa,"&#39;").replace(ha,"&#0;");else{if(!ia.test(a))return a;-1!=a.indexOf("&")&&(a=a.replace(v,"&amp;"));-1!=a.indexOf("<")&&
(a=a.replace(ca,"&lt;"));-1!=a.indexOf(">")&&(a=a.replace(da,"&gt;"));-1!=a.indexOf('"')&&(a=a.replace(ea,"&quot;"));-1!=a.indexOf("'")&&(a=a.replace(fa,"&#39;"));-1!=a.indexOf("\x00")&&(a=a.replace(ha,"&#0;"))}return a},v=/&/g,ca=/</g,da=/>/g,ea=/"/g,fa=/'/g,ha=/\x00/g,ia=/[\x00&<>"']/,w=function(a,b){return a<b?-1:a>b?1:0},ka=function(a){return String(a).replace(/\-([a-z])/g,function(a,d){return d.toUpperCase()})},la=function(a,b){b=m(b)?String(b).replace(/([-()\[\]{}+?*.$\^|,:#<!\\])/g,"\\$1").replace(/\x08/g,
"\\x08"):"\\s";return a.replace(new RegExp("(^"+(b?"|["+b+"]+":"")+")([a-z])","g"),function(a,b,e){return b+e.toUpperCase()})};var x=function(a,b){b.unshift(a);t.call(this,ba.apply(null,b));b.shift()};r(x,t);x.prototype.name="AssertionError";var y=function(a,b,d){if(!a){var c="Assertion failed";if(b){c+=": "+b;var e=Array.prototype.slice.call(arguments,2)}throw new x(""+c,e||[]);}return a};var ma=Array.prototype.indexOf?function(a,b,d){y(null!=a.length);return Array.prototype.indexOf.call(a,b,d)}:function(a,b,d){d=null==d?0:0>d?Math.max(0,a.length+d):d;if(m(a))return m(b)&&1==b.length?a.indexOf(b,d):-1;for(;d<a.length;d++)if(d in a&&a[d]===b)return d;return-1},na=Array.prototype.forEach?function(a,b,d){y(null!=a.length);Array.prototype.forEach.call(a,b,d)}:function(a,b,d){for(var c=a.length,e=m(a)?a.split(""):a,f=0;f<c;f++)f in e&&b.call(d,e[f],f,a)},oa=function(a){var b=a.length;if(0<
b){for(var d=Array(b),c=0;c<b;c++)d[c]=a[c];return d}return[]};var z;a:{var pa=l.navigator;if(pa){var qa=pa.userAgent;if(qa){z=qa;break a}}z=""};var ra=function(a,b,d){for(var c in a)b.call(d,a[c],c,a)},sa="constructor hasOwnProperty isPrototypeOf propertyIsEnumerable toLocaleString toString valueOf".split(" "),ta=function(a,b){for(var d,c,e=1;e<arguments.length;e++){c=arguments[e];for(d in c)a[d]=c[d];for(var f=0;f<sa.length;f++)d=sa[f],Object.prototype.hasOwnProperty.call(c,d)&&(a[d]=c[d])}};var A=function(a){A[" "](a);return a};A[" "]=n;var ua=function(a,b,d,c){c=c?c(b):b;return Object.prototype.hasOwnProperty.call(a,c)?a[c]:a[c]=d(b)};var B=-1!=z.indexOf("Opera"),C=-1!=z.indexOf("Trident")||-1!=z.indexOf("MSIE"),va=-1!=z.indexOf("Edge"),D=-1!=z.indexOf("Gecko")&&!(-1!=z.toLowerCase().indexOf("webkit")&&-1==z.indexOf("Edge"))&&!(-1!=z.indexOf("Trident")||-1!=z.indexOf("MSIE"))&&-1==z.indexOf("Edge"),E=-1!=z.toLowerCase().indexOf("webkit")&&-1==z.indexOf("Edge"),wa=function(){var a=l.document;return a?a.documentMode:void 0},F;
a:{var G="",H=function(){var a=z;if(D)return/rv\:([^\);]+)(\)|;)/.exec(a);if(va)return/Edge\/([\d\.]+)/.exec(a);if(C)return/\b(?:MSIE|rv)[: ]([^\);]+)(\)|;)/.exec(a);if(E)return/WebKit\/(\S+)/.exec(a);if(B)return/(?:Version)[ \/]?(\S+)/.exec(a)}();H&&(G=H?H[1]:"");if(C){var I=wa();if(null!=I&&I>parseFloat(G)){F=String(I);break a}}F=G}
var xa=F,ya={},J=function(a){return ua(ya,a,function(){for(var b=0,d=u(String(xa)).split("."),c=u(String(a)).split("."),e=Math.max(d.length,c.length),f=0;0==b&&f<e;f++){var g=d[f]||"",h=c[f]||"";do{g=/(\d*)(\D*)(.*)/.exec(g)||["","","",""];h=/(\d*)(\D*)(.*)/.exec(h)||["","","",""];if(0==g[0].length&&0==h[0].length)break;b=w(0==g[1].length?0:parseInt(g[1],10),0==h[1].length?0:parseInt(h[1],10))||w(0==g[2].length,0==h[2].length)||w(g[2],h[2]);g=g[3];h=h[3]}while(0==b)}return 0<=b})},K;var za=l.document;
K=za&&C?wa()||("CSS1Compat"==za.compatMode?parseInt(xa,10):5):void 0;var Aa=!C||9<=Number(K);!D&&!C||C&&9<=Number(K)||D&&J("1.9.1");C&&J("9");var L=function(a,b){return m(b)?a.getElementById(b):b},M=function(a,b,d,c){a=c||a;var e=b&&"*"!=b?String(b).toUpperCase():"";if(a.querySelectorAll&&a.querySelector&&(e||d))return a.querySelectorAll(e+(d?"."+d:""));if(d&&a.getElementsByClassName){b=a.getElementsByClassName(d);if(e){a={};for(var f=c=0,g;g=b[f];f++)e==g.nodeName&&(a[c++]=g);a.length=c;return a}return b}b=a.getElementsByTagName(e||"*");if(d){a={};for(f=c=0;g=b[f];f++){e=g.className;var h;if(h="function"==typeof e.split)h=0<=ma(e.split(/\s+/),
d);h&&(a[c++]=g)}a.length=c;return a}return b},Ca=function(a,b){ra(b,function(b,c){b&&b.H&&(b=b.G());"style"==c?a.style.cssText=b:"class"==c?a.className=b:"for"==c?a.htmlFor=b:Ba.hasOwnProperty(c)?a.setAttribute(Ba[c],b):0==c.lastIndexOf("aria-",0)||0==c.lastIndexOf("data-",0)?a.setAttribute(c,b):a[c]=b})},Ba={cellpadding:"cellPadding",cellspacing:"cellSpacing",colspan:"colSpan",frameborder:"frameBorder",height:"height",maxlength:"maxLength",nonce:"nonce",role:"role",rowspan:"rowSpan",type:"type",
usemap:"useMap",valign:"vAlign",width:"width"},Ea=function(a,b,d){var c=arguments,e=String(c[0]),f=c[1];if(!Aa&&f&&(f.name||f.type)){e=["<",e];f.name&&e.push(' name="',ja(f.name),'"');if(f.type){e.push(' type="',ja(f.type),'"');var g={};ta(g,f);delete g.type;f=g}e.push(">");e=e.join("")}e=document.createElement(e);f&&(m(f)?e.className=f:"array"==p(f)?e.className=f.join(" "):Ca(e,f));2<c.length&&Da(document,e,c,2);return e},Da=function(a,b,d,c){function e(c){c&&b.appendChild(m(c)?a.createTextNode(c):
c)}for(;c<d.length;c++){var f=d[c];if(!aa(f)||q(f)&&0<f.nodeType)e(f);else{a:{if(f&&"number"==typeof f.length){if(q(f)){var g="function"==typeof f.item||"string"==typeof f.item;break a}if("function"==p(f)){g="function"==typeof f.item;break a}}g=!1}na(g?oa(f):f,e)}}};var Fa=function(a){var b=a.type;switch(m(b)&&b.toLowerCase()){case "checkbox":case "radio":return a.checked?a.value:null;case "select-one":return b=a.selectedIndex,0<=b?a.options[b].value:null;case "select-multiple":b=[];for(var d,c=0;d=a.options[c];c++)d.selected&&b.push(d.value);return b.length?b:null;default:return null!=a.value?a.value:null}};var Ga=!C||9<=Number(K),Ha=C&&!J("9");!E||J("528");D&&J("1.9b")||C&&J("8")||B&&J("9.5")||E&&J("528");D&&!J("8")||C&&J("9");var Ia=function(){if(!l.addEventListener||!Object.defineProperty)return!1;var a=!1,b=Object.defineProperty({},"passive",{get:function(){a=!0}});l.addEventListener("test",n,b);l.removeEventListener("test",n,b);return a}();var N=function(a,b){this.type=a;this.currentTarget=this.target=b;this.defaultPrevented=this.v=!1};N.prototype.preventDefault=function(){this.defaultPrevented=!0};var O=function(a,b){N.call(this,a?a.type:"");this.relatedTarget=this.currentTarget=this.target=null;this.button=this.screenY=this.screenX=this.clientY=this.clientX=this.offsetY=this.offsetX=0;this.key="";this.charCode=this.keyCode=0;this.metaKey=this.shiftKey=this.altKey=this.ctrlKey=!1;this.s=this.state=null;a&&this.A(a,b)};r(O,N);
O.prototype.A=function(a,b){var d=this.type=a.type,c=a.changedTouches?a.changedTouches[0]:null;this.target=a.target||a.srcElement;this.currentTarget=b;if(b=a.relatedTarget){if(D){a:{try{A(b.nodeName);var e=!0;break a}catch(f){}e=!1}e||(b=null)}}else"mouseover"==d?b=a.fromElement:"mouseout"==d&&(b=a.toElement);this.relatedTarget=b;null===c?(this.offsetX=E||void 0!==a.offsetX?a.offsetX:a.layerX,this.offsetY=E||void 0!==a.offsetY?a.offsetY:a.layerY,this.clientX=void 0!==a.clientX?a.clientX:a.pageX,this.clientY=
void 0!==a.clientY?a.clientY:a.pageY,this.screenX=a.screenX||0,this.screenY=a.screenY||0):(this.clientX=void 0!==c.clientX?c.clientX:c.pageX,this.clientY=void 0!==c.clientY?c.clientY:c.pageY,this.screenX=c.screenX||0,this.screenY=c.screenY||0);this.button=a.button;this.keyCode=a.keyCode||0;this.key=a.key||"";this.charCode=a.charCode||("keypress"==d?a.keyCode:0);this.ctrlKey=a.ctrlKey;this.altKey=a.altKey;this.shiftKey=a.shiftKey;this.metaKey=a.metaKey;this.state=a.state;this.s=a;a.defaultPrevented&&
this.preventDefault()};O.prototype.preventDefault=function(){O.C.preventDefault.call(this);var a=this.s;if(a.preventDefault)a.preventDefault();else if(a.returnValue=!1,Ha)try{if(a.ctrlKey||112<=a.keyCode&&123>=a.keyCode)a.keyCode=-1}catch(b){}};var P="closure_listenable_"+(1E6*Math.random()|0),Ja=0;var Ka=function(a,b,d,c,e,f){this.listener=a;this.i=b;this.src=d;this.type=c;this.capture=!!e;this.m=f;this.key=++Ja;this.g=this.l=!1};Ka.prototype.u=function(){this.g=!0;this.m=this.src=this.i=this.listener=null};var Q=function(a){this.src=a;this.b={};this.o=0};Q.prototype.add=function(a,b,d,c,e){var f=a.toString();a=this.b[f];a||(a=this.b[f]=[],this.o++);var g;a:{for(g=0;g<a.length;++g){var h=a[g];if(!h.g&&h.listener==b&&h.capture==!!c&&h.m==e)break a}g=-1}-1<g?(b=a[g],d||(b.l=!1)):(b=new Ka(b,null,this.src,f,!!c,e),b.l=d,a.push(b));return b};
Q.prototype.B=function(a){var b=a.type;if(!(b in this.b))return!1;var d=this.b[b],c=ma(d,a),e;if(e=0<=c)y(null!=d.length),Array.prototype.splice.call(d,c,1);e&&(a.u(),0==this.b[b].length&&(delete this.b[b],this.o--));return e};var R="closure_lm_"+(1E6*Math.random()|0),S={},La=0,T=function(a,b,d,c,e){if(c&&c.once)return Ma(a,b,d,c,e);if("array"==p(b)){for(var f=0;f<b.length;f++)T(a,b[f],d,c,e);return null}d=Na(d);return a&&a[P]?a.I(b,d,q(c)?!!c.capture:!!c,e):Oa(a,b,d,!1,c,e)},Oa=function(a,b,d,c,e,f){if(!b)throw Error("Invalid event type");var g=q(e)?!!e.capture:!!e,h=U(a);h||(a[R]=h=new Q(a));d=h.add(b,d,c,g,f);if(d.i)return d;c=Pa();d.i=c;c.src=a;c.listener=d;if(a.addEventListener)Ia||(e=g),void 0===e&&(e=!1),a.addEventListener(b.toString(),
c,e);else if(a.attachEvent)a.attachEvent(Qa(b.toString()),c);else throw Error("addEventListener and attachEvent are unavailable.");La++;return d},Pa=function(){var a=Ra,b=Ga?function(d){return a.call(b.src,b.listener,d)}:function(d){d=a.call(b.src,b.listener,d);if(!d)return d};return b},Ma=function(a,b,d,c,e){if("array"==p(b)){for(var f=0;f<b.length;f++)Ma(a,b[f],d,c,e);return null}d=Na(d);return a&&a[P]?a.J(b,d,q(c)?!!c.capture:!!c,e):Oa(a,b,d,!0,c,e)},Qa=function(a){return a in S?S[a]:S[a]="on"+
a},Ta=function(a,b,d,c){var e=!0;if(a=U(a))if(b=a.b[b.toString()])for(b=b.concat(),a=0;a<b.length;a++){var f=b[a];f&&f.capture==d&&!f.g&&(f=Sa(f,c),e=e&&!1!==f)}return e},Sa=function(a,b){var d=a.listener,c=a.m||a.src;if(a.l&&"number"!=typeof a&&a&&!a.g){var e=a.src;if(e&&e[P])e.K(a);else{var f=a.type,g=a.i;e.removeEventListener?e.removeEventListener(f,g,a.capture):e.detachEvent&&e.detachEvent(Qa(f),g);La--;(f=U(e))?(f.B(a),0==f.o&&(f.src=null,e[R]=null)):a.u()}}return d.call(c,b)},Ra=function(a,
b){if(a.g)return!0;if(!Ga){if(!b)a:{b=["window","event"];for(var d=l,c=0;c<b.length;c++)if(d=d[b[c]],null==d){b=null;break a}b=d}c=b;b=new O(c,this);d=!0;if(!(0>c.keyCode||void 0!=c.returnValue)){a:{var e=!1;if(0==c.keyCode)try{c.keyCode=-1;break a}catch(g){e=!0}if(e||void 0==c.returnValue)c.returnValue=!0}c=[];for(e=b.currentTarget;e;e=e.parentNode)c.push(e);a=a.type;for(e=c.length-1;!b.v&&0<=e;e--){b.currentTarget=c[e];var f=Ta(c[e],a,!0,b);d=d&&f}for(e=0;!b.v&&e<c.length;e++)b.currentTarget=c[e],
f=Ta(c[e],a,!1,b),d=d&&f}return d}return Sa(a,new O(b,this))},U=function(a){a=a[R];return a instanceof Q?a:null},V="__closure_events_fn_"+(1E9*Math.random()>>>0),Na=function(a){y(a,"Listener can not be null.");if("function"==p(a))return a;y(a.handleEvent,"An object listener must have handleEvent method.");a[V]||(a[V]=function(b){return a.handleEvent(b)});return a[V]};var Va=function(a,b,d){var c=Ua[d];if(!c){var e=ka(d);c=e;void 0===a.style[e]&&(e=(E?"Webkit":D?"Moz":C?"ms":B?"O":null)+la(e),void 0!==a.style[e]&&(c=e));Ua[d]=c}(d=c)&&(a.style[d]=b)},Ua={};var W=function(a,b){var d=[];1<arguments.length&&(d=Array.prototype.slice.call(arguments).slice(1));var c=M(document,"th","tct-selectall",a);if(0!=c.length){c=c[0];var e=0,f=M(document,"tbody",null,a);f.length&&(e=f[0].rows.length);this.c=Ea("INPUT",{type:"checkbox"});c.appendChild(this.c);e?T(this.c,"click",this.D,!1,this):this.c.disabled=!0;this.f=[];this.h=[];this.j=[];c=M(document,"input",null,a);for(e=0;f=c[e];e++)"checkbox"==f.type&&f!=this.c?(this.f.push(f),T(f,"click",this.w,!1,this)):"action"==
f.name&&(0<=d.indexOf(f.value)?this.j.push(f):this.h.push(f),f.disabled=!0)}};k=W.prototype;k.f=null;k.a=0;k.c=null;k.h=null;k.j=null;k.D=function(a){for(var b=a.target.checked,d=a=0,c;c=this.f[d];d++)c.checked=b,a+=1;this.a=b?this.f.length:0;for(d=0;b=this.h[d];d++)b.disabled=!this.a;for(d=0;b=this.j[d];d++)b.disabled=1!=a?!0:!1};
k.w=function(a){this.a+=a.target.checked?1:-1;this.c.checked=this.a==this.f.length;a=0;for(var b;b=this.h[a];a++)b.disabled=!this.a;for(a=0;b=this.j[a];a++)b.disabled=1!=this.a?!0:!1};var Wa=function(){var a=L(document,"kinds");a&&new W(a);(a=L(document,"pending_backups"))&&new W(a);(a=L(document,"backups"))&&new W(a,"Restore");var b=L(document,"ae-datastore-admin-filesystem");b&&T(b,"change",function(){var a="gs"==Fa(b);L(document,"gs_bucket_tr").style.display=a?"":"none"});if(a=L(document,"confirm_delete_form")){var d=L(document,"confirm_readonly_delete");d&&(a.onsubmit=function(){var a=L(document,"confirm_message");if(m("color"))Va(a,"red","color");else for(var b in"color")Va(a,
"color"[b],b);return d.checked})}},X=["ae","Datastore","Admin","init"],Y=l;X[0]in Y||!Y.execScript||Y.execScript("var "+X[0]);for(var Z;X.length&&(Z=X.shift());)X.length||void 0===Wa?Y=Y[Z]&&Y[Z]!==Object.prototype[Z]?Y[Z]:Y[Z]={}:Y[Z]=Wa;
