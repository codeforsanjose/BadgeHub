
var SERVER_ENDPOINT = '/print';


var nametag = {
    canvas : null,
    margin_pct : 0.05,

    init : function (canvas_id, form_id, logo_elem, img_preview_id){
        this.canvas = document.getElementById(canvas_id);
        this.canvas_height = this.canvas.height;
        this.canvas_width = this.canvas.width;
        this.margin = this.margin_pct * this.canvas.width;

        this.logo = document.getElementById(logo_elem);
        this.form = document.getElementById(form_id);
        this.img_preview = document.getElementById(img_preview_id);
        this.name_elem = this.form.elements["name"];
        this.pronoun_elem = this.form.elements["pronoun"];
        this.email_elem = this.form.elements["email"];
        this.nametag_img_elem = this.form.elements["nametag_img"];

        if (this.canvas.getContext) {
            var self = this;
            function createNametag(){
                if (self.name_elem.value === '' &&
                    self.pronoun_elem.value === '' &&
                    self.email_elem.value === ''){
                    self.canvas.parentElement.classList.add('hidden')
                    return;
                }
                self.canvas.parentElement.classList.remove('hidden')
                self.draw();
            }
            this.name_elem.onkeyup = createNametag;
            this.pronoun_elem.onkeyup = createNametag;
            this.email_elem.onkeyup = createNametag;
            this.form.addEventListener('change', createNametag);
        } else {
          console.error('unsupported browser');
        }
    },

    draw : function(){
        this.clear_canvas();

        // top-center
        this.draw_text();
        this.reset_context();

        // lower-left corner
        this.draw_qr();
        this.reset_context();

        // lower-right
        this.draw_logo();
        this.reset_context();

        this.save_canvas();
    },

    reset_context : function(){
        var ctx = this.canvas.getContext('2d');
        ctx.fillStyle = "rgb(0,0,0)";
    },
    
    clear_canvas : function(){
        var ctx = this.canvas.getContext('2d');
        var c_height = this.canvas.height;
        var c_width = this.canvas.width;
        ctx.clearRect(0, 0, c_width, c_height);
        
        ctx.mozImageSmoothingEnabled = false;
        ctx.webkitImageSmoothingEnabled = false;
        ctx.msImageSmoothingEnabled = false;
        ctx.imageSmoothingEnabled = false;
    },

    save_canvas : function(){
        var img = this.canvas.toDataURL("image/png");
        this.img_preview.src=img;
        this.nametag_img_elem.value=img;
    },

    draw_text : function(){
        var ctx = this.canvas.getContext('2d');
        var c_height = this.canvas.height;
        var c_width = this.canvas.width;
        
        var text = this.name_elem.value + '(' + this.pronoun_elem.value + ')';
        var fontface = 'sans-serif';

        // fit text on canvas
        // http://stackoverflow.com/a/20552063
	// start with a large font size
        var fontsize=Math.floor(c_height/4);

        // lower the font size until the text fits the canvas
        do{
          fontsize = fontsize - 1;
          ctx.font=fontsize+"px "+fontface;
        } while (ctx.measureText(text).width > (c_width - (this.margin*2)))

        // draw the text
        ctx.fillText(text,this.margin, this.margin+fontsize);
    },

    draw_qr : function(){
        var ctx = this.canvas.getContext('2d');
        var c_height = this.canvas.height;
        var c_width = this.canvas.width;

         if (this.name_elem.value === '' &&
             this.pronoun_elem.value === '' &&
             this.email_elem.value === ''){
                return;
         }
                                 
        var qr_text = this.name_elem.value + ';' + this.pronoun_elem.value + ';' + this.email_elem.value;
  
        // cell size
        var cs=Math.floor(c_height/70);
        
        // max bit limit for types:
        // 2 : 128
        // 3 : 208
        // 4 : 288
        // 5 : 368
        // 9 : 800
        // library max typeNumber is 40
        var typeNumber = 3;
        if (qr_text.length < 5) {
            typeNumber = 1;
        } else if (qr_text.length >= 5 && qr_text.length < 15) {
            typeNumber = 2;
        } else if (qr_text.length >= 15 && qr_text.length < 25) {
           typeNumber  = 3;
        } else if (qr_text.length >= 25 && qr_text.length < 35) {
            typeNumber = 4;
        } else if (qr_text.length >= 35 && qr_text.length < 45) {
            typeNumber = 5;
        } else if (qr_text.length >= 45 && qr_text.length < 55) {
            typeNumber = 6;
        }
        var qr = new QRCode(typeNumber, QRErrorCorrectLevel.H);
        qr.addData(qr_text);
        qr.make();
        var qr_pos = [0 + this.margin, c_height - this.margin - (qr.getModuleCount()*cs)];
        for (var r = 0; r < qr.getModuleCount(); r++) {
            for (var c = 0; c < qr.getModuleCount(); c++) {
                if (qr.isDark(r, c) ) {
                    ctx.fillStyle = "rgb(0,0,0)";  
                } else {
                    ctx.fillStyle = "rgb(255,255,255)";  
                }
                ctx.fillRect (c*cs + qr_pos[0], r*cs + qr_pos[1],cs,cs);  
            }   
        }
    },

    draw_logo : function(){
        var ctx = this.canvas.getContext('2d');
        var c_height = this.canvas.height;
        var c_width = this.canvas.width;

        // TODO: adjust image height/width based on a percentage
        // of the canvas height/width and image height/width
        var img = this.logo;
        // lower-right corner
	var image_size = this.calculateAspectRatioFit(img.width, img.height, (c_width*.5), (c_height*.5))
        var x_pos = c_width - image_size.width - this.margin;
        var y_pos = c_height - image_size.height - this.margin;
        ctx.drawImage(img, x_pos, y_pos, image_size.width, image_size.height);

        // convert to greyscale
        // http://www.htmlgoodies.com/html5/javascript/display-images-in-black-and-white-using-the-html5-canvas.html
        var px = ctx.getImageData(x_pos, y_pos, image_size.width, image_size.height);
        var pixels  = px.data;
        for (var i = 0, n = pixels.length; i < n; i += 4) {
            var grayscale = pixels[i] * .3 + pixels[i+1] * .59 + pixels[i+2] * .11;
            pixels[i  ] = grayscale;        // red
            pixels[i+1] = grayscale;        // green
            pixels[i+2] = grayscale;        // blue
            //pixels[i+3]              is alpha
        }
        ctx.putImageData(px, x_pos, y_pos);
    },

    calculateAspectRatioFit : function(srcWidth, srcHeight, maxWidth, maxHeight) {
        // http://stackoverflow.com/a/14731922
        var ratio = Math.min(maxWidth / srcWidth, maxHeight / srcHeight);
        return { width: srcWidth*ratio, height: srcHeight*ratio };
    }
};


(function(){
    nametag.init('nametag_canvas', 'login_form', 'c4sj_logo', 'nametag_preview_surrogate');
})();
