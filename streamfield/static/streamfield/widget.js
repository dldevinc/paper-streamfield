/* global gettext */

(function($) {

    function StreamBlock(element) {
        this.$widget = $(element);
        this.$container = this.$widget.find(".stream-field__container");
        this.$control = this.$widget.find("textarea");
        this.init();
    }

    StreamBlock.prototype.init = function() {
        const value = this.$control.val();

        this.showPreloader();

        $.ajax({
            method: "POST",
            url: this.$widget.data("renderUrl"),
            contentType: "application/json",
            data: value,
            dataType: "json",
        }).done(response => {
            if (response.status === "OK") {
                this.$container.html(response.html);
            }
        });
    }

    StreamBlock.prototype.showPreloader = function() {
        this.$container.html(
            `<div class="spinner-border text-info" role="status">
              <span class="sr-only">${gettext("Loading...")}</span>
            </div>`
        );
    }


    $(document).ready(() => {
        $(".stream-field").each((index, element) => {
            new StreamBlock(element);
        });
    });

})(django.jQuery);
