
var SERVER_ENDPOINT = '/print';

var nametag = {
    canvas : null,
    margin : 15,

    init : function (canvas_id, form_id, logo_elem){
        this.canvas = document.getElementById(canvas_id);
        this.canvas_height = this.canvas.height;
        this.canvas_width = this.canvas.width;

        this.logo = document.getElementById(logo_elem);
        this.form = document.getElementById(form_id);
        this.name_elem = this.form.elements["name"];
        this.email_elem = this.form.elements["email"];
        this.nametag_img_elem = this.form.elements["nametag_img"];

        if (this.canvas.getContext) {
            var self = this;
            function createNametag(){
                if (self.name_elem.value === '' &&
                    self.email_elem.value === ''){
                    self.canvas.parentElement.classList.add('hidden')
                    return;
                }
                self.canvas.parentElement.classList.remove('hidden')
                self.draw();
            }
            this.name_elem.onkeyup = createNametag;
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
        this.nametag_img_elem.value=img;
    },

    draw_text : function(){
        var ctx = this.canvas.getContext('2d');
        var c_height = this.canvas.height;
        var c_width = this.canvas.width;
        
        var text = this.name_elem.value;
        var font_size = 48;
        if (text.length > 15){
          font_size = 30;
        }
        ctx.font = font_size+'px sans-serif';
        ctx.fillText(text, this.margin, this.margin+font_size);
    },

    draw_qr : function(){
        var ctx = this.canvas.getContext('2d');
        var c_height = this.canvas.height;
        var c_width = this.canvas.width;

         if (this.name_elem.value === '' &&
             this.email_elem.value === ''){
                return;
         }
                                 
        var qr_text = this.name_elem.value + ';' + this.email_elem.value;
  
        var cs=3; // cell size
        
        // max bit limit for types:
        // 2 : 128
        // 3 : 208
        // 4 : 288
        // 5 : 368
        // 9 : 800
        var typeNumber = 3;
        if (qr_text.length < 25){
           typeNumber  = 3;
        } else if (qr_text.length >= 25 && qr_text.length < 35) {
            typeNumber = 4;
        } else if (qr_text.length >= 35) {
            typeNumber = 5;
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
        var i_width = parseInt(img.width)*.8;
        var i_height = parseInt(img.height)*.8;
        // lower-right corner
        var x_pos = c_width - i_width - this.margin;
        var y_pos = c_height - i_height - this.margin;
        ctx.drawImage(img, x_pos, y_pos, i_width, i_height);

        // convert to greyscale
        // http://www.htmlgoodies.com/html5/javascript/display-images-in-black-and-white-using-the-html5-canvas.html
        var px = ctx.getImageData(x_pos, y_pos, i_width, i_height);
        var pixels  = px.data;
        for (var i = 0, n = pixels.length; i < n; i += 4) {
            var grayscale = pixels[i] * .3 + pixels[i+1] * .59 + pixels[i+2] * .11;
            pixels[i  ] = grayscale;        // red
            pixels[i+1] = grayscale;        // green
            pixels[i+2] = grayscale;        // blue
            //pixels[i+3]              is alpha
        }
        ctx.putImageData(px, x_pos, y_pos);
    }
};


(function(){
    nametag.init('nametag_canvas', 'login_form', 'c4sj_logo');
})();
