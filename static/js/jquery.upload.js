<<<<<<< HEAD
jQuery.fn.extend({
    upload: function (url, inputName, callback) {
        var $o = $(this);
        if (!inputName) { inputName = "file"; }

        if ($("#upload_file_iframe").length == 0) {
            $("body").append('<iframe style="display:none; width:0px; height;0px;" id="upload_file_iframe" name="upload_file_iframe"></iframe>');
        }

        var $form = $('<form method="POST" class="upload_file" target="upload_file_iframe" name="upload_file_form" enctype="multipart/form-data" style="position:relative;overflow:hidden;"></form>');
        $form.attr("action", url);
        var $uploader = $('<input name="' + inputName + '" title="单击选择" type="file" style="position:absolute; visibility:visible; outline-width:medium; outline-style:none; outline-color:initial; opacity:0; filter:alpha(opacity:0); cursor:pointer;" />');
        $o.wrap($form).after($uploader);

        $uploader.change(function () {
            $o.parents(".upload_file").submit();
            callback();
        });

        $o.mousemove(function (e) {
            $uploader.css({
                "left": e.pageX - $o.parents(".upload_file").offset().left - $uploader.width() + 10,
                "top": e.pageY - $o.parents(".upload_file").offset().top - $uploader.height() / 2
            });
        });

        $uploader.mousemove(function (e) {
            $uploader.css({
                "left": e.pageX - $o.parents(".upload_file").offset().left - $uploader.width() + 10,
                "top": e.pageY - $o.parents(".upload_file").offset().top - $uploader.height() / 2
            });
        });
    }
=======
jQuery.fn.extend({
    upload: function (url, inputName, callback) {
        var $o = $(this);
        if (!inputName) { inputName = "file"; }

        if ($("#upload_file_iframe").length == 0) {
            $("body").append('<iframe style="display:none; width:0px; height;0px;" id="upload_file_iframe" name="upload_file_iframe"></iframe>');
        }

        var $form = $('<form method="POST" class="upload_file" target="upload_file_iframe" name="upload_file_form" enctype="multipart/form-data" style="position:relative;overflow:hidden;"></form>');
        $form.attr("action", url);
        var $uploader = $('<input name="' + inputName + '" title="单击选择" type="file" style="position:absolute; visibility:visible; outline-width:medium; outline-style:none; outline-color:initial; opacity:0; filter:alpha(opacity:0); cursor:pointer;" />');
        $o.wrap($form).after($uploader);

        $uploader.change(function () {
            $o.parents(".upload_file").submit();
            callback();
        });

        $o.mousemove(function (e) {
            $uploader.css({
                "left": e.pageX - $o.parents(".upload_file").offset().left - $uploader.width() + 10,
                "top": e.pageY - $o.parents(".upload_file").offset().top - $uploader.height() / 2
            });
        });

        $uploader.mousemove(function (e) {
            $uploader.css({
                "left": e.pageX - $o.parents(".upload_file").offset().left - $uploader.width() + 10,
                "top": e.pageY - $o.parents(".upload_file").offset().top - $uploader.height() / 2
            });
        });
    }
>>>>>>> 903cf25d870f2cbcd68c2b4adc2f597bf9c9405a
});