

PAGE_HEIGHT_JS = """
    var body = document.body;
    var html = document.documentElement;
    var height = Math.max(body.scrollHeight, body.offsetHeight, html.clientHeight, html.scrollHeight, html.offsetHeight);
    return height;
"""


CLEAR_CANVAS_JS = """
    var canvas = document.getElementById("myCanvas");
    var ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);
"""


ADD_FRAGMENT_JS = """
    function create(htmlStr) {
        var frag = document.createDocumentFragment(),
            temp = document.createElement('div');
        temp.innerHTML = htmlStr;
        while (temp.firstChild) {
            frag.appendChild(temp.firstChild);
        }
        return frag;
    }

    var fragment = create('%s');
    document.body.insertBefore(fragment, %s);
"""

DRAW_LINE_JS = """
    var c = document.getElementById("myCanvas");
    var context = c.getContext("2d");
    context.beginPath();
    context.strokeStyle="%s";
    context.moveTo(%s, %s);
    context.lineTo(%s, %s);
    context.stroke();
    context.closePath();
"""

DRAW_RECT_JS = """
    var c = document.getElementById("myCanvas");
    var ctx = c.getContext("2d");
    ctx.beginPath();
    ctx.strokeStyle="%(colour)s";
    ctx.rect(%(x)s,%(y)s,%(width)s,%(height)s);
    ctx.stroke();
    ctx.closePath();
"""

DRAW_TEXT_JS = """
    var c = document.getElementById("myCanvas");
    var ctx = c.getContext("2d");
    ctx.font="%spx Georgia";
    ctx.fillStyle="%s";
    ctx.fillText("%s",%s,%s);
"""

DRAW_MULTIPLE_RECTS_JS = """
    var c = document.getElementById("myCanvas");
    var ctx = c.getContext("2d");
    var boxes = %s;
    for (var i in boxes) {
        box = boxes[i];
        ctx.beginPath();
        ctx.strokeStyle="%s";
        ctx.rect(box[0], box[1], box[2], box[3]);
        ctx.stroke();
        ctx.closePath();
    }
"""

PRELOAD_JS = {
    'getOuterHTML_js_multiple': """
    function(){
        var get_func = function(){
            var aa="function"==typeof Object.defineProperties?Object.defineProperty:function(a,c,b){if(b.get||b.set)throw new TypeError("ES3 does not support getters and setters.");a!=Array.prototype&&a!=Object.prototype&&(a[c]=b.value)},ba="undefined"!=typeof window&&window===this?this:"undefined"!=typeof global?global:this;\nfunction e(a,c){if(c){for(var b=ba,d=a.split("."),f=0;f<d.length-1;f++){var h=d[f];h in b||(b[h]={});b=b[h]}d=d[d.length-1];f=b[d];h=c(f);h!=f&&null!=h&&aa(b,d,{configurable:!0,writable:!0,value:h})}}\ne("String.prototype.repeat",function(a){return a?a:function(a){var b;if(null==this)throw new TypeError("The \'this\' value for String.prototype.repeat must not be null or undefined");b=this+"";if(0>a||1342177279<a)throw new RangeError("Invalid count value");a|=0;for(var d="";a;)if(a&1&&(d+=b),a>>>=1)b+=b;return d}});e("Math.sign",function(a){return a?a:function(a){a=Number(a);return!a||isNaN(a)?a:0<a?1:-1}});var g=this;function l(a){return"string"==typeof a};function m(a,c){this.a=n[a]||p;this.message=c||"";var b=this.a.replace(/((?:^|\\s+)[a-z])/g,function(a){return a.toUpperCase().replace(/^[\\s\\xa0]+/g,"")}),d=b.length-5;if(0>d||b.indexOf("Error",d)!=d)b+="Error";this.name=b;b=Error(this.message);b.name=this.name;this.stack=b.stack||""}\n(function(){var a=Error;function c(){}c.prototype=a.prototype;m.b=a.prototype;m.prototype=new c;m.prototype.constructor=m;m.a=function(b,c,f){for(var h=Array(arguments.length-2),k=2;k<arguments.length;k++)h[k-2]=arguments[k];return a.prototype[c].apply(b,h)}})();var p="unknown error",n={15:"element not selectable",11:"element not visible"};n[31]=p;n[30]=p;n[24]="invalid cookie domain";n[29]="invalid element coordinates";n[12]="invalid element state";n[32]="invalid selector";n[51]="invalid selector";\nn[52]="invalid selector";n[17]="javascript error";n[405]="unsupported operation";n[34]="move target out of bounds";n[27]="no such alert";n[7]="no such element";n[8]="no such frame";n[23]="no such window";n[28]="script timeout";n[33]="session not created";n[10]="stale element reference";n[21]="timeout";n[25]="unable to set cookie";n[26]="unexpected alert open";n[13]=p;n[9]="unknown command";m.prototype.toString=function(){return this.name+": "+this.message};var q=String.prototype.trim?function(a){return a.trim()}:function(a){return a.replace(/^[\\s\\xa0]+|[\\s\\xa0]+$/g,"")};\nfunction r(a,c){for(var b=0,d=q(String(a)).split("."),f=q(String(c)).split("."),h=Math.max(d.length,f.length),k=0;!b&&k<h;k++){var S=d[k]||"",ja=f[k]||"",ka=RegExp("(\\\\d*)(\\\\D*)","g"),la=RegExp("(\\\\d*)(\\\\D*)","g");do{var t=ka.exec(S)||["","",""],u=la.exec(ja)||["","",""];if(0==t[0].length&&0==u[0].length)break;b=v(0==t[1].length?0:parseInt(t[1],10),0==u[1].length?0:parseInt(u[1],10))||v(0==t[2].length,0==u[2].length)||v(t[2],u[2])}while(!b)}return b}function v(a,c){return a<c?-1:a>c?1:0};var w;a:{var x=g.navigator;if(x){var y=x.userAgent;if(y){w=y;break a}}w=""}function z(a){return-1!=w.indexOf(a)};function ca(a,c){for(var b=a.length,d=l(a)?a.split(""):a,f=0;f<b;f++)f in d&&c.call(void 0,d[f],f,a)};function A(){return z("iPhone")&&!z("iPod")&&!z("iPad")};function B(){return z("Opera")||z("OPR")}function C(){return(z("Chrome")||z("CriOS"))&&!B()&&!z("Edge")};var D=B(),E=z("Trident")||z("MSIE"),F=z("Edge"),G=z("Gecko")&&!(-1!=w.toLowerCase().indexOf("webkit")&&!z("Edge"))&&!(z("Trident")||z("MSIE"))&&!z("Edge"),da=-1!=w.toLowerCase().indexOf("webkit")&&!z("Edge");function ea(){var a=w;if(G)return/rv\\:([^\\);]+)(\\)|;)/.exec(a);if(F)return/Edge\\/([\\d\\.]+)/.exec(a);if(E)return/\\b(?:MSIE|rv)[: ]([^\\);]+)(\\)|;)/.exec(a);if(da)return/WebKit\\/(\\S+)/.exec(a)}function H(){var a=g.document;return a?a.documentMode:void 0}\nvar I=function(){if(D&&g.opera){var a;var c=g.opera.version;try{a=c()}catch(b){a=c}return a}a="";(c=ea())&&(a=c?c[1]:"");return E&&(c=H(),null!=c&&c>parseFloat(a))?String(c):a}(),J={},K=g.document,L=K&&E?H()||("CSS1Compat"==K.compatMode?parseInt(I,10):5):void 0;!G&&!E||E&&9<=Number(L)||G&&(J["1.9.1"]||(J["1.9.1"]=0<=r(I,"1.9.1")));E&&(J["9"]||(J["9"]=0<=r(I,"9")));var fa=z("Firefox"),ga=A()||z("iPod"),ha=z("iPad"),M=z("Android")&&!(C()||z("Firefox")||B()||z("Silk")),ia=C(),N=z("Safari")&&!(C()||z("Coast")||B()||z("Edge")||z("Silk")||z("Android"))&&!(A()||z("iPad")||z("iPod"));var ma={SCRIPT:1,STYLE:1,HEAD:1,IFRAME:1,OBJECT:1},na={IMG:" ",BR:"\\n"};function oa(a,c,b){if(!(a.nodeName in ma))if(3==a.nodeType)b?c.push(String(a.nodeValue).replace(/(\\r\\n|\\r|\\n)/g,"")):c.push(a.nodeValue);else if(a.nodeName in na)c.push(na[a.nodeName]);else for(a=a.firstChild;a;)oa(a,c,b),a=a.nextSibling};function O(a){return(a=a.exec(w))?a[1]:""}var pa=function(){if(fa)return O(/Firefox\\/([0-9.]+)/);if(E||F||D)return I;if(ia)return O(/Chrome\\/([0-9.]+)/);if(N&&!(A()||z("iPad")||z("iPod")))return O(/Version\\/([0-9.]+)/);if(ga||ha){var a=/Version\\/(\\S+).*Mobile\\/(\\S+)/.exec(w);if(a)return a[1]+"."+a[2]}else if(M)return(a=O(/Android\\s+([0-9.]+)/))?a:O(/Version\\/([0-9.]+)/);return""}();var qa;function P(a){ra?qa(a):M?r(sa,a):r(pa,a)}var ra=function(){if(!G)return!1;var a=g.Components;if(!a)return!1;try{if(!a.classes)return!1}catch(f){return!1}var c=a.classes,a=a.interfaces,b=c["@mozilla.org/xpcom/version-comparator;1"].getService(a.nsIVersionComparator),d=c["@mozilla.org/xre/app-info;1"].getService(a.nsIXULAppInfo).version;qa=function(a){b.compare(d,""+a)};return!0}(),Q;if(M){var ta=/Android\\s+([0-9\\.]+)/.exec(w);Q=ta?ta[1]:"0"}else Q="0";\nvar sa=Q,ua=E&&!(8<=Number(L)),va=E&&!(9<=Number(L));M&&P(2.3);M&&P(4);N&&P(6);function R(a,c){c=c.toLowerCase();if("style"==c)return wa(a.style.cssText);if(ua&&"value"==c&&T(a,"INPUT"))return a.value;if(va&&!0===a[c])return String(a.getAttribute(c));var b=a.getAttributeNode(c);return b&&b.specified?b.value:null}var xa=/[;]+(?=(?:(?:[^"]*"){2})*[^"]*$)(?=(?:(?:[^\']*\'){2})*[^\']*$)(?=(?:[^()]*\\([^()]*\\))*[^()]*$)/;\nfunction wa(a){var c=[];ca(a.split(xa),function(a){var d=a.indexOf(":");0<d&&(a=[a.slice(0,d),a.slice(d+1)],2==a.length&&c.push(a[0].toLowerCase(),":",a[1],";"))});c=c.join("");return c=";"==c.charAt(c.length-1)?c:c+";"}function U(a,c){var b;ua&&"value"==c&&T(a,"OPTION")&&null===R(a,"value")?(b=[],oa(a,b,!1),b=b.join("")):b=a[c];return b}function T(a,c){return!!a&&1==a.nodeType&&(!c||a.tagName.toUpperCase()==c)}\nfunction ya(a){return T(a,"OPTION")?!0:T(a,"INPUT")?(a=a.type.toLowerCase(),"checkbox"==a||"radio"==a):!1};var za={"class":"className",readonly:"readOnly"},V="async autofocus autoplay checked compact complete controls declare defaultchecked defaultselected defer disabled draggable ended formnovalidate hidden indeterminate iscontenteditable ismap itemscope loop multiple muted nohref noresize noshade novalidate nowrap open paused pubdate readonly required reversed scoped seamless seeking selected spellcheck truespeed willvalidate".split(" ");function Aa(a,c){var b=null,d=c.toLowerCase();if("style"==d)return(b=a.style)&&!l(b)&&(b=b.cssText),b;if(("selected"==d||"checked"==d)&&ya(a)){if(!ya(a))throw new m(15,"Element is not selectable");var b="selected",f=a.type&&a.type.toLowerCase();if("checkbox"==f||"radio"==f)b="checked";return U(a,b)?"true":null}var h=T(a,"A");if(T(a,"IMG")&&"src"==d||h&&"href"==d)return(b=R(a,d))&&(b=U(a,d)),b;if("spellcheck"==d){b=R(a,d);if(null!==b){if("false"==b.toLowerCase())return"false";if("true"==b.toLowerCase())return"true"}return U(a,\nd)+""}h=za[c]||c;a:if(l(V))d=l(d)&&1==d.length?V.indexOf(d,0):-1;else{for(var k=0;k<V.length;k++)if(k in V&&V[k]===d){d=k;break a}d=-1}if(0<=d)return(b=null!==R(a,c)||U(a,h))?"true":null;try{f=U(a,h)}catch(S){}(d=null==f)||(d=typeof f,d="object"==d&&null!=f||"function"==d);d?b=R(a,c):b=f;return null!=b?b.toString():null}var W=["_"],X=g;W[0]in X||!X.execScript||X.execScript("var "+W[0]);for(var Y;W.length&&(Y=W.shift());){var Z;if(Z=!W.length)Z=void 0!==Aa;Z?X[Y]=Aa:X[Y]?X=X[Y]:X=X[Y]={}};; return this._.apply(null,arguments);
            }
        var windowDict = {navigator:typeof window!=\'undefined\'?window.navigator:null,document:typeof window!=\'undefined\'?window.document:null}

        results = new Array(arguments.length);

        for (i = 0; i < arguments.length; i++) {
            results[i] = get_func.apply(windowDict, new Array(arguments[i], "outerHTML"));
        }
        return results;
    }\n
    """,
    'getRect_multiple_js': """
        function(){

            results = new Array(arguments.length);

            for (i = 0; i < arguments.length; i++) {
                var elem = arguments[i];
                results[i] = elem.getBoundingClientRect();
            }
            return results;
        }\n
    """,
    'get_xpaths': """
        function(){

            function getPathTo(element) {
                var tagName = element.tagName.toLowerCase();
                if (element===document.body || tagName == "body")
                    return tagName

                var ix= 0;
                var siblings= element.parentNode.childNodes;
                for (var i= 0; i<siblings.length; i++) {
                    var sibling= siblings[i];
                    if (sibling===element)
                        return getPathTo(element.parentNode)+'/'+tagName+'['+(ix+1)+']';
                    if (sibling.nodeType===1 && sibling.tagName.toLowerCase()===tagName)
                        ix++;
                }
            }
            results = [];
            for(i=0; i < arguments.length; i++){
                   results.push(getPathTo(arguments[i]));
            }
            return results;
        }
    """,
    'get_parent_paths': """
    function(){

        function getElemDict(element) {

            return {
                'elem': element, 'tag_name': element.tagName.toLowerCase(),
                'outer_html': element.outerHTML
            }

            var id = null;
            if(element.id !== '')
                id = element.id;

            var other_attrs = {};
            for (var att, i = 0, atts = element.attributes, n = atts.length; i < n; i++){
                att = atts[i];
                if (att.nodeName == 'class')
                    continue;
                other_attrs[att.nodeName] = att.nodeValue;
            }

            return {
                'tag_name': element.tagName.toLowerCase(),
                'id': id, 'other_attrs': other_attrs,
                'class_attr': element.getAttribute('class'),
                'elem': element,
            }            
        }

        function getPathTo(element) {

            if (element===document.body)
                return [getElemDict(element)];

            var ix= 0;
            var siblings= element.parentNode.childNodes;
            for (var i= 0; i < siblings.length; i++) {
                var sibling= siblings[i];
                if (sibling===element)
                    return getPathTo(element.parentNode).concat([getElemDict(element)]);
                if (sibling.nodeType===1 && sibling.tagName===element.tagName)
                    ix++;
            }
        }
        results = [];
        for(i=0; i < arguments.length; i++){
            var path = getPathTo(arguments[i]);
            path = path.reverse();
            results.push(path);
        }
        return results;
    }
    """,
    'getComputedCss_multiple_js': """
        function(){

            var valuesEncountered = new Object();

            function getStyleProperties(style){
                var result = new Object();
                for(var i=0; i<style.length; i++){
                    var key = style[i];
                    var val = style[key];
                    if(val == "none" || val == "auto" || val == null)
                        continue;
                    result[key] = val;

                    var valKey = key + "___" + (val.toString());
                    valuesEncountered[valKey] = (valuesEncountered[valKey] || 0) + 1;
                }
                return result;
            }

            // no longer used
            function removeCommonValues(res){
                var toRemove = ["transform-origin", "perspective-origin"]; // also remove these noisey values

                var ignoreKeys = ["color", "font-size", "font-weight", "visibility", "display"];
                for(var key in valuesEncountered){
                    var count = valuesEncountered[key];
                    if( count == res.length )
                        toRemove.push(key.split("___")[0]);
                }
                for(var i=0; i < toRemove.length; i++){
                    var key = toRemove[i];
                    for(var j=0; j < res.length; j++){
                        var di = res[j]["all_computed_styles"];
                        delete di[key];
                    }
                }
            }

            jqueryElems = $(arguments);
            hiddenElems = jqueryElems.filter(":hidden");

            results = new Array(arguments.length);
            for (var i = 0; i < arguments.length; i++) {
                 styleObj = window.getComputedStyle(arguments[i]);
                 results[i] = {
                    "all_computed_styles": getStyleProperties(styleObj),
                    "color": styleObj["color"],
                    "font-size": styleObj["font-size"],
                    "font-weight": styleObj["font-weight"],
                    "visibility": styleObj["visibility"],
                    "is_visible_jquery": hiddenElems.index(arguments[i]) == -1,  //$(arguments[i]).is(':visible')),
                    "display": styleObj["display"],
                 };
                 if(i == arguments.length-1)
                    results[i]["encountered"] = valuesEncountered;
            }

            return results;
        }
    """,
}
