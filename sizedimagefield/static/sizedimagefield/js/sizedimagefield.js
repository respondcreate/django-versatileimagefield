$(function () {
    $('img.sizedimage-preview').click(function (e) {
        // Creating a canvas when the image is clicked
        if (!this.canvas) {
            this.canvas = $('<canvas/>').css({
                width: this.width + 'px',
                height: this.height + 'px'
            })[0];
            this.canvas.getContext('2d').drawImage(this, 0, 0, this.width, this.height);
        }
        // Figuring out where on the X/Y grid was clicked where the
        // max values for X/Y are 1 and min values are 0
        var x_coord = parseFloat(event.offsetX / this.width).toFixed(2);
        var y_coord = parseFloat(event.offsetY / this.height).toFixed(2);
        var containing_div = $(this).parents('div.sizedimagefield');
        var hidden_input = containing_div.children('input.centerpoint-input');
        hidden_input.val(x_coord + 'x' + y_coord);
    });
});
