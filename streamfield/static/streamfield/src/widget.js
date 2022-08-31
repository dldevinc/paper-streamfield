/* global gettext */

import "./widget.scss";

const Sortable = window.paperAdmin.Sortable;
const Widget = window.paperAdmin.Widget;
const modals = window.paperAdmin.modals;


class StreamField {
    constructor(element) {
        this.field = element;
        this.container = this.field.querySelector(".stream-field__container");
        this.control = this.field.querySelector(".stream-field__control");

        this.blockMap = this.buildBlockMap();
        this._initSortable();

        this.render(this.control.value);
    }

    destroy() {
        // TODO
    }

    buildBlockMap() {
        let value;

        try {
            value = JSON.parse(this.control.value);
        } catch {
            value = {};
        }

        const result = {};
        for (const record of value) {
            result[record["uuid"]] = record;
        }
        return result
    }

    _initSortable() {
        return Sortable.create(this.container, {
            animation: 0,
            draggable: ".stream-field__block",
            handle: ".stream-field__sortable-handler",
            ghostClass: "sortable-ghost",
            onEnd: () => {
                this.save();
            }
        });
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
        return fetch(renderUrl, {
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
            this.container.innerHTML = data.html || "";
        }).catch(reason => {
            if (reason instanceof Error) {
                // JS-ошибки дублируем в консоль
                console.error(reason);
            }
            modals.showErrors(reason);
        });
    }

    save() {
        const newValue = Array.from(this.container.querySelectorAll(".stream-field__block")).map(block => {
            const uuid = block.dataset.uuid;
            return this.blockMap[uuid];
        }).filter(Boolean);
        this.control.value = JSON.stringify(newValue);
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
