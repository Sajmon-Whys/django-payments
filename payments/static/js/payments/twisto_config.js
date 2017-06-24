var _twisto_config = {
            public_key: document.getElementByName('public_key').value,
            script: 'https://static.twisto.cz/api/v2/twisto.js',
    };
(function(e,g,a){function h(a){return function(){b._.push([a,arguments])}}var f=["check"],b=e||{},c=document.createElement(a);a=document.getElementsByTagName(a)[0];b._=[];for(var d=0;d<f.length;d++)b[f[d]]=h(f[d]);this[g]=b;c.type="text/javascript";c.async=!0;c.src=e.script;a.parentNode.insertBefore(c,a);delete e.script}).call(window,_twisto_config,"Twisto","script");
