/* global gettext */

import "./widget.scss";

const Sortable = window.paperAdmin.Sortable;
const Widget = window.paperAdmin.Widget;
const modals = window.paperAdmin.modals;


class StreamField {
    static STATUS = {
        LOADING: "loading",
        READY: "ready"
    };

    static CSS = {
        field: "stream-field",
        input: "stream-field__control",
        container: "stream-field__container",
        block: "stream-field__block"
    };

    constructor(element) {
        this.field = element;
        this.container = this.field.querySelector(`.${this.CSS.container}`);
        this.control = this.field.querySelector(`.${this.CSS.input}`);

        this.blockMap = this.buildBlockMap();
        this._sortable = this._initSortable();
        this._addEventListeners();

        this.render(this.control.value);
    }

    get STATUS() {
        return this.constructor.STATUS;
    }

    get CSS() {
        return this.constructor.CSS;
    }

    /**
     * @returns {string}
     */
    getStatus() {
        return Object.values(this.STATUS).find(value => {
            return this.field.classList.contains(`${this.CSS.field}--${value}`);
        });
    }

    /**
     * @param {string} status
     */
    setStatus(status) {
        Object.values(this.STATUS).forEach(value => {
            this.field.classList.toggle(`${this.CSS.field}--${value}`, status === value);
        });
    }

    /**
     * @returns {HTMLElement[]}
     */
    getBlocks() {
        return Array.from(this.container.querySelectorAll(`.${this.CSS.block}`))
    }

    destroy() {
        if (this._sortable) {
            this._sortable.destroy();
        }

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
            filter: (event, target) => {
                const status = this.getStatus();
                if (status === this.STATUS.LOADING) {
                    return true;
                }

                if (!target) {
                    return true;
                }
            },
            handle: ".stream-field__sortable-handler",
            ghostClass: "sortable-ghost",
            onEnd: () => {
                this.save();
            }
        });
    }

    _addEventListeners() {
        this.field.addEventListener("click", event => {
            const deleteButton = event.target.closest(".stream-field__delete-btn");
            if (!deleteButton) {
                return
            }

            const block = event.target.closest(".stream-field__block");
            block.classList.add("stream-field__block--removing");
            // TODO
        });
    }

    render(json_data) {
        this.setStatus(this.STATUS.LOADING);

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
            this.setStatus(this.STATUS.READY);
        }).catch(reason => {
            if (reason instanceof Error) {
                // JS-ошибки дублируем в консоль
                console.error(reason);
            }
            modals.showErrors(reason);
            this.setStatus(this.STATUS.READY);
        });
    }

    save() {
        const newValue = this.getBlocks().map(block => {
            const uuid = block.dataset.uuid;
            return this.blockMap[uuid];
        });
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
