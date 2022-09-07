/* global gettext */
import Mustache from 'mustache';

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
        control: "stream-field__control",
        blocks: "stream-field__blocks",
        block: "stream-field__block",
        sortableHandler: "stream-field__sortable-handler",
        deleteBlockButton: "stream-field__delete-btn",
        changeBlockButton: "stream-field__change-btn",
        addNewBlockButton: "stream-field__add-block-btn",
        lookupBlockButton: "stream-field__lookup-block-btn",
    };

    constructor(element) {
        this.field = element;
        this.control = this.field.querySelector(`.${this.CSS.control}`);
        this.blocks = this.field.querySelector(`.${this.CSS.blocks}`);

        this.allowedModels = JSON.parse(this.control.dataset.allowedModels);
        this.blockMap = this.buildBlockMap();
        this._sortable = this._initSortable();
        this._addListeners();

        this.update();
    }

    get STATUS() {
        return this.constructor.STATUS;
    }

    get CSS() {
        return this.constructor.CSS;
    }

    /**
     * @returns {Array}
     */
    get value() {
        let data;
        try {
            data = JSON.parse(this.control.value);
        } catch {
            data = [];
        }
        return data
    }

    /**
     * @param {string|Array} data
     */
    set value(data) {
        if (typeof data !== "string") {
            data = JSON.stringify(data);
        }
        this.control.value = data;
    }

    /**
     * @returns {string}
     */
    get status() {
        return Object.values(this.STATUS).find(value => {
            return this.field.classList.contains(`${this.CSS.field}--${value}`);
        });
    }

    /**
     * @param {string} status
     */
    set status(status) {
        Object.values(this.STATUS).forEach(value => {
            this.field.classList.toggle(`${this.CSS.field}--${value}`, status === value);
        });

        const addNewBlockButton = this.field.querySelector(`.${this.CSS.addNewBlockButton}`);
        const lookupBlockButton = this.field.querySelector(`.${this.CSS.lookupBlockButton}`);
        addNewBlockButton && (addNewBlockButton.disabled = !(status === this.STATUS.READY));
        lookupBlockButton && (lookupBlockButton.disabled = !(status === this.STATUS.READY));
    }

    /**
     * @returns {HTMLElement[]}
     */
    getBlocks() {
        return Array.from(this.blocks.querySelectorAll(`.${this.CSS.block}`))
    }

    destroy() {
        if (this._sortable) {
            this._sortable.destroy();
        }

        // TODO
    }

    /**
     * Создаёт объект для быстрого поиска блоков по UUID.
     * @returns {Object}
     */
    buildBlockMap() {
        const result = {};
        for (const record of this.value) {
            result[record["uuid"]] = record;
        }
        return result
    }

    /**
     * @returns {*}
     * @private
     */
    _initSortable() {
        return Sortable.create(this.blocks, {
            animation: 0,
            draggable: `.${this.CSS.block}`,
            filter: (event, target) => {
                if (this.status === this.STATUS.LOADING) {
                    return true;
                }

                if (!target) {
                    return true;
                }
            },
            handle: `.${this.CSS.sortableHandler}`,
            ghostClass: "sortable-ghost",
            onEnd: () => {
                this.save();
            }
        });
    }

    _addListeners() {
        this.field.addEventListener("click", event => {
            const deleteButton = event.target.closest(`.${this.CSS.deleteBlockButton}`);
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

            const changeButton = event.target.closest(`.${this.CSS.changeBlockButton}`);
            if (changeButton) {
                event.preventDefault();
                const jQueryEvent = $.Event("django:show-related", {href: changeButton.href});
                $(changeButton).trigger(jQueryEvent);
                if (!jQueryEvent.isDefaultPrevented()) {
                    showStreamBlockPopup(changeButton);
                }
            }

            const addButton = event.target.closest(`.${this.CSS.addNewBlockButton}`);
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

    renderStream(data) {
        this.status = this.STATUS.LOADING;

        const renderUrl = this.field.dataset.renderStreamUrl;
        return fetch(renderUrl, {
            method: "POST",
            mode: "same-origin",
            cache: "no-store",
            headers: {
                "Content-Type": "application/json;charset=utf-8"
            },
            body: JSON.stringify(data)
        }).then(response => {
            if (!response.ok) {
                throw `${response.status} ${response.statusText}`;
            }
            return response.json()
        }).then(response => {
            const rendered = [];
            response.blocks.forEach(block => {
                const status = block.status;
                const template = this.field.querySelector(`.stream-field__block-template--${status}`);
                if (!template) {
                    return
                }

                rendered.push(
                    Mustache.render(template.innerHTML, block)
                )
            });
            this.blocks.innerHTML = rendered.join("");

            this.status = this.STATUS.READY;
        }).catch(reason => {
            if (reason instanceof Error) {
                // JS-ошибки дублируем в консоль
                console.error(reason);
            }
            modals.showErrors(reason);
            this.status = this.STATUS.READY;
        });
    }

    save() {
        this.value = this.getBlocks().map(block => {
            const uuid = block.dataset.uuid;
            return this.blockMap[uuid];
        });
    }

    update() {
        return this.renderStream(this.value);
    }
}


class StreamFieldWidget extends Widget {
    _init(element) {
        element._streamField = new StreamField(element, this);
    }

    _destroy(element) {
        if (element._streamField) {
            element._streamField.destroy();
            delete element._streamField;
        }
    }

    getStreamFieldInstance(element) {
        return element._streamField;
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
