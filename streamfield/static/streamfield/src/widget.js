/* global gettext */

import "./widget.scss";

const Sortable = window.paperAdmin.Sortable;
const Widget = window.paperAdmin.Widget;


class StreamField {
    constructor(element) {
        this.field = element;
        this.container = this.field.querySelector(".stream-field__container");
        this.control = this.field.querySelector(".stream-field__control");

        this.render(this.control.value);
    }

    destroy() {
        // TODO
    }

    showPreloader() {
        this.container.innerHTML =
            `<div class="spinner-border text-info" role="status">
              <span class="sr-only">${gettext("Loading...")}</span>
            </div>`;
    }

    render(json_data) {
        this.showPreloader();

        const renderUrl = this.field.dataset.renderUrl;
        fetch(renderUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json;charset=utf-8"
            },
            body: json_data
        }).then(response => {
            if (!response.ok) {
                throw `${response.status} ${response.statusText}`;
            }
            return response.json()
        }).then(data => {
            if (data.status === "OK") {
                this.container.innerHTML = data.html;
            }
        });
    }
}


class StreamFieldWidget extends Widget {
    _init(element) {
        element.__streamFieldInstance = new StreamField(element, this);
    }

    _destroy(element) {
        if (element.__streamFieldInstance) {
            element.__streamFieldInstance.destroy();
            delete element.__streamFieldInstance;
        }
    }
}


const widget = new StreamFieldWidget();
widget.observe(".stream-field");
widget.initAll(".stream-field");
