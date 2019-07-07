
function Nametag(config){
    this.canvas = config['canvas_elem'];
    this.print_dpi = 300;
    this.canvas_height = this.canvas.height;
    this.canvas_width = this.canvas.width;
    this.margin_pct = 0.05;
    this.margin_px = this.margin_pct * this.canvas.width;
    this.nametag_scale_global = config['nametag_scale_global'] || 0.5

    this.text_x_offset_pct = config['text_x_offset_pct'] || 0.66
    this.text_y_offset_pct = config['text_y_offset_pct'] || 0.4
    this.show_text_line1 = config['show_text_line1'] || true
    this.show_text_line2 = config['show_text_line2'] || false

    this.logo_scale = config['logo_scale'] || 0.5;
    this.logo_x_offset_pct = config['logo_x_offset_pct'] || 0.66
    this.logo_y_offset_pct = config['logo_y_offset_pct'] || 0.4

    this.qr_max_width_pct =  config['qr_max_width_pct'] || 0.25;
    this.qr_x_offset_pct = config['qr_x_offset_pct'] || 0.05
    this.qr_y_offset_pct = config['qr_y_offset_pct'] || 0.9

    this.logo = config['logo_elem'];
    this.form = config['form_elem'];
    this.img_preview = config['img_preview_elem'];
    this.name_elem = config['line_1_input']
    this.pronoun_elems = config['pronoun_elems']
    this.enable_pronouns = config['enable_pronouns']
    this.email_elem = config['line_2_input']
    this.img_form_elem = config['img_form_elem']

    this.show_diag = config['show_diag'] || false

    this.img_resize_dummy = document.createElement('img')
    this.canvas.parentNode.insertBefore(this.img_resize_dummy, this.canvas);

    if (this.canvas.getContext) {
        var self = this;
        function createNametag(){
            if (self.name_elem.value === '' &&
                self.email_elem.value === '' &&
                self.email_elem.value === ''){
                self.canvas.parentElement.classList.add('hidden')
                return;
            }
            self.canvas.parentElement.classList.remove('hidden')
            self.draw();
        }
        this.name_elem.onkeyup = createNametag;
        this.pronoun_elems.onkeyup = createNametag;

        for (var i = 0; i < this.pronoun_elems.length; i++) {
            this.pronoun_elems[i].addEventListener('change', createNametag);
        }

        this.email_elem.onkeyup = createNametag;
        if (this.form) {
            this.form.addEventListener('change', createNametag);
        }
    } else {
      console.error('unsupported browser');
    }
}

Nametag.prototype = {

    set_logo_pos : function(x_offset_pct, y_offset_pct){
        this.logo_x_offset_pct = x_offset_pct;
        this.logo_y_offset_pct = y_offset_pct;
    },

    set_text_pos : function(x_offset_pct, y_offset_pct){
        this.text_x_offset_pct = x_offset_pct
        this.text_y_offset_pct = y_offset_pct
    },

    set_text_x_offset_pct : function(x_offset_pct){
        this.text_x_offset_pct = x_offset_pct
        this.draw()
    },

    set_text_y_offset_pct : function(y_offset_pct){
        this.text_y_offset_pct = y_offset_pct
        this.draw()
    },

    set_logo_x_pos : function(x_offset_pct){
        this.logo_x_offset_pct = x_offset_pct;
        this.draw()
    },

    set_logo_y_pos : function(y_offset_pct){
        this.logo_y_offset_pct = y_offset_pct;
        this.draw()
    },

    set_qr_x_pos : function(x_offset_pct){
        this.qr_x_offset_pct = x_offset_pct;
        this.draw()
    },

    set_qr_y_pos : function(y_offset_pct){
        this.qr_y_offset_pct = y_offset_pct;
        this.draw()
    },

    set_logo_scale : function(factor){
        this.logo_scale = factor
        this.draw()
    },

    set_pronouns_enabled : function(enabled){
        console.log('setting pronouns to be '+(enabled? 'enabled' : 'disabled'))
        this.enable_pronouns = enabled;
        this.draw();
    },

    show_safe_zone : function(show_diag){
        this.show_diag=show_diag
        this.draw()
    },

    set_qr_max_width_pct : function(width_pct){
        this.qr_max_width_pct = width_pct
        this.draw()
    },

    draw : function(){
        this.clear_canvas();

        this.draw_text();
        this.reset_context();

        this.draw_qr();
        this.reset_context();

        this.draw_logo();
        this.reset_context();

        this.draw_diag_lines();

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
        
        ctx.mozImageSmoothingEnabled = true;
        ctx.webkitImageSmoothingEnabled = true;
        ctx.msImageSmoothingEnabled = true;
        ctx.imageSmoothingEnabled = true;
    },

    save_canvas : function(){
        var img = this.canvas.toDataURL("image/png");
        if (this.img_preview) {
            this.img_preview.src=img;
        }
        if (this.img_form_elem) {
            this.img_form_elem.value=img;
        } else {
            console.warn('No form element available for the image data; printing will not function.')
        }
    },

    draw_text : function(){
        var ctx = this.canvas.getContext('2d');
        var c_height = this.canvas.height;
        var c_width = this.canvas.width;

        var text_line1 =  this.name_elem.value;

        if (this.enable_pronouns) {
            for (var i=0; i < this.pronoun_elems.length; i++) {
                if (this.pronoun_elems[i].checked) {
                    text_line1 += ' (' + this.pronoun_elems[i].value + ')';
                }
            }
        }
        var text_line2 = this.email_elem.value;
        // var fontface = 'sans-serif';
        var fontface = 'Roboto';

        // fit text on canvas
        // http://stackoverflow.com/a/20552063
        // start with a large font size
        var fontsize= Math.floor(c_height/6);
        var textDimensions = 0

        // lower the font size until the text fits the canvas
        do {
          textDimensions = ctx.measureText(text_line1)
          fontsize = fontsize - 1;
          ctx.font=fontsize+"px "+fontface;
        } while (textDimensions.width > Math.floor(c_width - (this.margin_px *2)))

        var calculatedHeight = this.determineFontHeightInPixels(ctx.font)
        console.log('font size: '+fontsize+', calc height: '+ calculatedHeight)

        // draw the text
        var text_line1_pos = this.positionInsideBoundaries([this.text_x_offset_pct, this.text_y_offset_pct],
            [textDimensions.width, calculatedHeight],
            [c_width, c_height], this.margin_px)
        console.log('text position: '+[text_line1_pos[0]]+','+text_line1_pos[1])

        if (this.show_diag) {
            this.drawLine('rgba(0,0,255,150)', text_line1_pos[0], text_line1_pos[1],
                text_line1_pos[0]+textDimensions.width, text_line1_pos[1])
            this.drawLine('rgba(0,0,255,150)', text_line1_pos[0], text_line1_pos[1]+calculatedHeight,
                text_line1_pos[0]+textDimensions.width, text_line1_pos[1]+calculatedHeight)
        }
        ctx.textBaseline='hanging'
        if (this.show_text_line1){
            ctx.fillText(text_line1, text_line1_pos[0], text_line1_pos[1]);
        }
        if (this.show_text_line2){
            ctx.fillText(text_line2, text_line1_pos[0], text_line1_pos[1]+fontsize);
        }
    },

    draw_qr : function(){
        var ctx = this.canvas.getContext('2d');
        var c_height = this.canvas.height;
        var c_width = this.canvas.width;

         if (this.name_elem.value === '' &&
             this.pronoun_elems.value === '' &&
             this.email_elem.value === ''){
                return;
         }
                                 
        var qr_text = this.name_elem.value + ';' + this.email_elem.value;

        if (this.enable_pronouns && this.pronoun_elems.value !== '') {
            for (var i=0; i < this.pronoun_elems.length; i++) {
                if (this.pronoun_elems[i].checked) {
                    qr_text += ';' + this.pronoun_elems[i].value;
                }
            }
        }

        // cell size
        var cs = 1;
        
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

        var max_qr_max_width_px = Math.floor(this.qr_max_width_pct*c_width)
        var qr = null;
        do {
            qr = new QRCode(typeNumber, QRErrorCorrectLevel.L);
            qr.addData(qr_text);
            qr.make();
            cs++;
        } while ((qr.getModuleCount()*cs) < max_qr_max_width_px)
        console.log('max QR width:'+max_qr_max_width_px+'px, QR width:'+(qr.getModuleCount()*cs)+'px')

        var qr_pos = this.positionInsideBoundaries([this.qr_x_offset_pct, this.qr_y_offset_pct],
            [(qr.getModuleCount()*cs), (qr.getModuleCount()*cs)],
            [c_width, c_height], this.margin_px)
        console.log('QR pos: ', qr_pos)
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
        console.log('canvas dimensions: { w:'+c_width+', h:'+c_height+' }')

        var img = this.logo;
        // the position is anchored in the top left corner
        var image_size = {
            width: img.width*this.logo_scale*this.nametag_scale_global,
            height: img.height*this.logo_scale*this.nametag_scale_global
        }
        console.log('image_size  { w:'+img.width+', h:'+img.height+'} '+
            ' -> x'+this.logo_scale*this.nametag_scale_global+' -> '+
            '{ w:'+image_size.width+', h:'+image_size.height+' }');

        var img_pos = this.positionInsideBoundaries([this.logo_x_offset_pct, this.logo_y_offset_pct],
            [image_size.width, image_size.height],
             [c_width, c_height], this.margin_px)

        console.log('image_pos : { x:'+img_pos[0]+', y:'+img_pos[1]+' }')
        ctx.drawImage(img, img_pos[0], img_pos[1], image_size.width, image_size.height);

        // convert to greyscale
        // http://www.htmlgoodies.com/html5/javascript/display-images-in-black-and-white-using-the-html5-canvas.html
        var px = ctx.getImageData(img_pos[0], img_pos[1], image_size.width, image_size.height);
        var pixels  = px.data;
        for (var i = 0, n = pixels.length; i < n; i += 4) {
            var greyscale = pixels[i] * .3 + pixels[i+1] * .59 + pixels[i+2] * .11;
            pixels[i  ] = greyscale;        // red
            pixels[i+1] = greyscale;        // green
            pixels[i+2] = greyscale;        // blue
            //pixels[i+3]              is alpha
        }
        ctx.putImageData(px, img_pos[0], img_pos[1]);
    },

    draw_diag_lines : function(){
        if (this.show_diag) {
            // center lines
            this.drawLine("rgba(255, 0, 0, 150)",
                this.canvas.width/2, 0,
                this.canvas.width/2, this.canvas.height)
            this.drawLine("rgba(255, 0, 0, 150)",
                0, this.canvas.height/2,
                this.canvas.width, this.canvas.height/2)
            // margins
            this.drawLine("rgba(0, 255, 0, 150)",
                0, this.margin_px,
                this.canvas.width, this.margin_px)
            this.drawLine("rgba(0, 255, 0, 150)",
                0, this.canvas.height - this.margin_px,
                this.canvas.width, this.canvas.height - this.margin_px)
            this.drawLine("rgba(0, 255, 0, 150)",
                this.margin_px, 0,
                this.margin_px, this.canvas.height)
            this.drawLine("rgba(0, 255, 0, 150)",
                this.canvas.width - this.margin_px, 0,
                this.canvas.width - this.margin_px, this.canvas.height)
        }
    },

    positionInsideBoundaries : function(obj_offset, obj_size, canvas_size, margin_px) {
        // keep the object inside the bounds of the image, considering the margins as well.
        usable_space = {'w': canvas_size[0] - (2 * margin_px), 'h': canvas_size[1] - (2 * margin_px)}
        obj_center = {'w': Math.floor(obj_size[0] * obj_offset[0]), 'h': Math.floor(obj_size[1] * obj_offset[1])}
        return [Math.floor(margin_px + ((obj_offset[0] * usable_space['w']) - obj_center['w'])),
                Math.floor(margin_px + ((obj_offset[1] * usable_space['h']) - obj_center['h']))]
    },

    drawLine : function(lineColor, startX, startY, endX, endY) {
        var ctx = this.canvas.getContext('2d');
        ctx.strokeStyle = lineColor;
        ctx.beginPath();
        ctx.moveTo(startX, startY);
        ctx.lineTo(endX, endY);
        ctx.stroke();
    },

    /**
    * https://stackoverflow.com/a/13730758/940217
    */
    determineFontHeightInPixels : function(fontStyle) {
        var result //= this.heightCache[fontStyle];
        if (!result) {
            var fontDraw = document.createElement("canvas");
            var ctx = fontDraw.getContext('2d');
            ctx.fillRect(0, 0, fontDraw.width, fontDraw.height);
            ctx.textBaseline = 'top';
            ctx.fillStyle = 'white';
            ctx.font = fontStyle;
            ctx.fillText('gM', 0, 0);
            var pixels = ctx.getImageData(0, 0, fontDraw.width, fontDraw.height).data;
            var start = -1;
            var end = -1;
            for (var row = 0; row < fontDraw.height; row++) {
                for (var column = 0; column < fontDraw.width; column++) {
                    var index = (row * fontDraw.width + column) * 4;
                    if (pixels[index] === 0) {
                        if (column === fontDraw.width - 1 && start !== -1) {
                            end = row;
                            row = fontDraw.height;
                            break;
                        }
                        continue;
                    }
                    else {
                        if (start === -1) {
                            start = row;
                        }
                        break;
                    }
                }
            }
            result = end - start;
            //this.heightCache[fontStyle] = result;
        }
        return result;
    }
};
