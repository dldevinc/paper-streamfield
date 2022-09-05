/* global gettext */

import "./widget.scss";

const Sortable = window.paperAdmin.Sortable;
const Widget = window.paperAdmin.Widget;
const popupUtils = window.paperAdmin.popupUtils;
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

    get value() {
        let data;
        try {
            data = JSON.parse(this.control.value);
        } catch {
            data = {};
        }
        return data
    }

    set value(data) {
        if (typeof data !== "string") {
            data = JSON.stringify(data);
        }
        this.control.value = data;
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
        const result = {};
        for (const record of this.value) {
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
            if (deleteButton) {
                event.preventDefault();
                deleteButton.disabled = true;

                modals.createModal({
                    modalClass: "paper-modal--warning fade",
                    title: gettext("Confirm deletion"),
                    body: gettext("Are you sure you want to <b>DELETE</b> selected block from this field?"),
                    buttons: [
                        {
                            label: gettext("Cancel"),
                            buttonClass: "btn-light",
                            onClick: (event, popup) => {
                                popup.destroy();
                            }
                        },
                        {
                            autofocus: true,
                            label: gettext("Delete"),
                            buttonClass: "btn-danger",
                            onClick: (event, popup) => {
                                popup.destroy();

                                const block = deleteButton.closest(`.${this.CSS.block}`);
                                block.remove();
                                this.save();
                                this.update();
                            }
                        }
                    ],
                    onInit: function() {
                        this.show();
                    },
                    onDestroy: function() {
                        deleteButton.disabled = false;
                    }
                });
            }

            const changeButton = event.target.closest(".stream-field__change-btn");
            if (changeButton) {
                event.preventDefault();
                const jQueryEvent = $.Event("django:show-related", {href: changeButton.href});
                $(changeButton).trigger(jQueryEvent);
                if (!jQueryEvent.isDefaultPrevented()) {
                    showStreamBlockPopup(changeButton);
                }
            }

            const addButton = event.target.closest(".stream-field__add-btn");
            if (addButton) {
                event.preventDefault();
                const jQueryEvent = $.Event("django:show-related", {href: changeButton.href});
                $(addButton).trigger(jQueryEvent);
                if (!jQueryEvent.isDefaultPrevented()) {
                    showStreamBlockPopup(addButton);
                }
            }
        });
    }

    render(data) {
        this.setStatus(this.STATUS.LOADING);

        if (typeof data !== "string") {
            data = JSON.stringify(data);
        }

        const renderUrl = this.field.dataset.renderUrl;
        return fetch(renderUrl, {
            method: "POST",
            mode: "same-origin",
            cache: "no-store",
            headers: {
                "Content-Type": "application/json;charset=utf-8"
            },
            body: data
        }).then(response => {
            if (!response.ok) {
                throw `${response.status} ${response.statusText}`;
            }
            return response.json()
        }).then(data => {
            this.container.innerHTML = data.rendered_field || "";
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
        this.value = this.getBlocks().map(block => {
            const uuid = block.dataset.uuid;
            return this.blockMap[uuid];
        });
    }

    update() {
        return this.render(this.value);
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

    getStreamFieldInstance(element) {
        return element.__streamFieldInstance;
    }
}


const widget = new StreamFieldWidget();
widget.observe(".stream-field");
widget.initAll(".stream-field");


/**
 * @param {HTMLElement} triggeringLink
 */
function showStreamBlockPopup(triggeringLink) {
    return popupUtils.showAdminPopup(triggeringLink, /^(change|add|delete)_/, true);
}

function dismissChangeStreamBlockPopup(win) {
    const name = "change_" + popupUtils.removePopupIndex(win.name);
    const element = document.getElementById(name);
    const fieldWrapper = element && element.closest(".paper-widget");
    const field = fieldWrapper && fieldWrapper.firstElementChild;
    const instance = field && widget.getStreamFieldInstance(field);

    instance.update();

    popupUtils.removeRelatedWindow(win);
    win.close();
}

window.dismissChangeStreamBlockPopup = dismissChangeStreamBlockPopup;
