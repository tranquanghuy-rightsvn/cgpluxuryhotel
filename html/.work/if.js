[...document.querySelectorAll("iframe")].map(f=>({src:f.src,name:f.name,id:f.id,r:f.getBoundingClientRect().toJSON()}))
