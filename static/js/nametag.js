
var SERVER_ENDPOINT = '/print';

var nametag = {
    canvas : null,

    init : function (canvas_id, form_id){
        this.canvas = document.getElementById(canvas_id);
        this.canvas_height = this.canvas.height;
        this.canvas_width = this.canvas.width;

        this.form = document.getElementById(form_id);
        this.name_elem = this.form.elements["name"];
        this.email_elem = this.form.elements["email"];
        this.nametag_img_elem = this.form.elements["nametag_img"];

        if (this.canvas.getContext) {
            var self = this;
            function createNametag(){
                self.draw();
                self.print();
            }
            this.form.addEventListener('change', createNametag);
        } else {
          console.error('unsupported browser');
        }
    },

    draw : function(){
        var ctx = this.canvas.getContext('2d');
        var c_height = this.canvas.height;
        var c_width = this.canvas.width;
        ctx.clearRect(0, 0, c_width, c_height);
        
        ctx.mozImageSmoothingEnabled = false;
        ctx.webkitImageSmoothingEnabled = false;
        ctx.msImageSmoothingEnabled = false;
        ctx.imageSmoothingEnabled = false;

        var img = new Image();
        img.onload = function() {
            // TODO: adjust image height/width based on a percentage
            // of the canvas height/width and image height/width
            var i_width = parseInt(img.width)/4;
            var i_height = parseInt(img.height)/4;
            var x_pos = c_width - i_width;
            var y_pos = c_height - i_height;
            console.log('drawing c4sj logo', {'x' : x_pos, 'y' : y_pos, 'w': i_width, 'h':i_height})
            ctx.drawImage(img, x_pos, y_pos, i_width, i_height);
        };
        img.src = 'static/images/c4sj_logo.jpg';

        ctx.font = '48px serif';
        ctx.fillText(this.name_elem.value, 10, 50);
        this.print();
    },

    print : function(){
        console.log('sending to the server for printing...')
        var img = this.canvas.toDataURL("image/png");
        document.getElementById("n_preview").src=img;
        this.nametag_img_elem.value=img;
    }
};

/*
function append_qrcode(typeNumber,elem_id,text) {
    // typeNumber is 4 or 9
    var e=document.getElementById(elem_id);
    if (e) {
        var canvas=document.createElement('canvas');
        
        var ctx = canvas.getContext('2d');
        
        var cs=4;// cell size
        var qr = new QRCode(typeNumber, QRErrorCorrectLevel.H);
        qr.addData(text);
        qr.make();

        canvas.setAttribute('width',qr.getModuleCount()*cs);
        canvas.setAttribute('height',qr.getModuleCount()*cs);
        e.appendChild(canvas);

        if (canvas.getContext){
            for (var r = 0; r < qr.getModuleCount(); r++) {
                for (var c = 0; c < qr.getModuleCount(); c++) {
                    if (qr.isDark(r, c) ) {
                        ctx.fillStyle = "rgb(0,0,0)";  
                    } else {
                        ctx.fillStyle = "rgb(255,255,255)";  
                    }
                    ctx.fillRect (c*cs,r*cs,cs,cs);  
                }   
            }

        }
    }
}
*/

(function(){
    nametag.init('nametag_canvas', 'login_form');
})();