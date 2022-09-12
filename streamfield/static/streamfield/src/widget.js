/* global gettext */
import Mustache from "mustache";
import {v4 as uuid4, validate as uuid_validate} from "uuid";

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
        toolbar: "stream-field__toolbar",
        sortableHandler: "stream-field__sortable-handler",
        createBlockButton: "stream-field__create-block-btn",
        lookupBlockButton: "stream-field__lookup-block-btn",
        changeBlockButton: "stream-field__change-btn",
        deleteBlockButton: "stream-field__delete-btn",
    };

    constructor(element) {
        this.field = element;
        this.control = this.field.querySelector(`.${this.CSS.control}`);
        this.blocks = this.field.querySelector(`.${this.CSS.blocks}`);
        this.toolbar = this.field.querySelector(`.${this.CSS.toolbar}`);

        this._sortable = this._initSortable();
        this._addListeners();
        this._updateBlockMap();

        this.wrapPreloader(Promise.all([
            this.update(),
            this.updateToolbar(),
        ]))
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
    }

    /**
     * @returns {String[]}
     */
    get allowedModels() {
        return JSON.parse(this.control.dataset.allowedModels);
    }

    /**
     * @returns {HTMLElement[]}
     */
    getBlocks() {
        return Array.from(this.blocks.querySelectorAll(`.${this.CSS.block}`))
    }

    /**
     * @param {string} uuid
     * @returns {Object}
     */
    getBlockByUUID(uuid) {
        return this._blockMap[uuid];
    }

    destroy() {
        if (this._sortable) {
            this._sortable.destroy();
        }

        // TODO: remove event listeners
    }

    /**
     * Создаёт объект для быстрого поиска блоков по UUID.
     *
     * @returns {Object}
     */
    _updateBlockMap() {
        let hasBadBlocks = false;
        const result = {};

        const processedValue = this.value.map(record => {
            let uuid = record["uuid"];
            if ((typeof uuid === "string") && uuid_validate(uuid)) {
                return result[uuid] = record;
            } else {
                hasBadBlocks = true;
                uuid = uuid4();
                return result[uuid] = {uuid: uuid};
            }
        });

        this._blockMap = result;
        if (processedValue) {
            this.value = processedValue;
        }
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
                                this.wrapPreloader(
                                    this.update()
                                );
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

            const lookupBlockButton = event.target.closest(`.${this.CSS.lookupBlockButton}`);
            if (lookupBlockButton) {
                event.preventDefault();
                const jQueryEvent = $.Event("django:show-related", {href: lookupBlockButton.href});
                $(lookupBlockButton).trigger(jQueryEvent);
                if (!jQueryEvent.isDefaultPrevented()) {
                    showStreamBlockPopup(lookupBlockButton);
                }
            }

            const createBlockButton = event.target.closest(`.${this.CSS.createBlockButton}`);
            if (createBlockButton) {
                event.preventDefault();
                const jQueryEvent = $.Event("django:show-related", {href: createBlockButton.href});
                $(createBlockButton).trigger(jQueryEvent);
                if (!jQueryEvent.isDefaultPrevented()) {
                    showStreamBlockPopup(createBlockButton);
                }
            }
        });
    }

    /**
     * @param {Object} block
     * @private
     */
    _appendBlock(block) {
        const uuid = block.uuid;
        if (!uuid_validate(uuid)) {
            throw new Error("Invalid UUID");
        }

        const newValue = this.value;
        newValue.push(block);
        this.value = newValue;

        this._blockMap[uuid] = block;
    }

    save() {
        this.value = this.getBlocks().map(block => {
            const uuid = block.dataset.uuid;
            return this.getBlockByUUID(uuid);
        });
    }

    update() {
        return this.renderStream(this.value);
    }

    /**
     * @param {Promise} promise
     * @returns {Promise}
     */
    wrapPreloader(promise) {
        this.status = this.STATUS.LOADING;
        return promise.finally(() => {
            this.status = this.STATUS.READY;
        })
    }

    renderStream(data) {
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
        }).catch(reason => {
            if (reason instanceof Error) {
                // JS-ошибки дублируем в консоль
                console.error(reason);
            }
            modals.showErrors(reason);
        });
    }

    renderToolbar(data) {
        const renderUrl = this.field.dataset.renderToolbarUrl;
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
            const template = this.field.querySelector(".stream-field__toolbar-button-template");
            if (!template) {
                return
            }

            const rendered = [];
            response.buttons.forEach(button => {
                rendered.push(
                    Mustache.render(template.innerHTML, button)
                )
            });

            this.toolbar.innerHTML = rendered.join("");
        });
    }

    updateToolbar() {
        return this.renderToolbar({
            "field_id": this.control.id,
            "models": this.allowedModels
        });
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
    return popupUtils.showAdminPopup(triggeringLink, /^(change|add|lookup)_/, true);
}

/**
 * @param {Window} win
 * @param {String} newId
 */
function dismissAddStreamBlockPopup(win, newId) {
    const name = popupUtils.removePopupIndex(win.name);
    const match = /^(.+)--(.+)\.(.+)$/.exec(name);
    if (match) {
        const control = document.getElementById(match[1]);
        const field = control.closest(".stream-field");
        const streamField = field && widget.getStreamFieldInstance(field);

        streamField._appendBlock({
            "uuid": uuid4(),
            "model": `${match[2]}.${match[3]}`,
            "pk": newId,
        });

        streamField.wrapPreloader(
            streamField.update()
        );

        popupUtils.removeRelatedWindow(win);
        win.close();
    }
}

/**
 * @param {Window} win
 */
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

/**
 * @param {Window} win
 * @param {String} objId
 */
function dismissDeleteStreamBlockPopup(win, objId) {
    const name = popupUtils.removePopupIndex(win.name);
    const match = /^(.+)--(.+)\.(.+)$/.exec(name);
    if (match) {
        const control = document.getElementById(match[1]);
        const field = control.closest(".stream-field");
        const streamField = field && widget.getStreamFieldInstance(field);

        streamField.wrapPreloader(
            streamField.update()
        );

        popupUtils.removeRelatedWindow(win);
        win.close();
    }
}

/**
 * Обёртка над Django-обработчиком `window.dismissRelatedLookupPopup`.
 * @param {Function} originalFunc
 */
function dismissLookupStreamBlockPopup(originalFunc) {
    return (win, chosenId) => {
        const name = popupUtils.removePopupIndex(win.name);
        const match = /^(.+)--(.+)\.(.+)$/.exec(name);
        if (match) {
            const control = document.getElementById(match[1]);
            const field = control.closest(".stream-field");
            const streamField = field && widget.getStreamFieldInstance(field);

            streamField._appendBlock({
                "uuid": uuid4(),
                "model": `${match[2]}.${match[3]}`,
                "pk": chosenId,
            });

            streamField.wrapPreloader(
                streamField.update()
            );

            popupUtils.removeRelatedWindow(win);
            win.close();
        } else {
            originalFunc(win, chosenId);
        }
    }
}

window.dismissAddStreamBlockPopup = dismissAddStreamBlockPopup;
window.dismissChangeStreamBlockPopup = dismissChangeStreamBlockPopup;
window.dismissDeleteStreamBlockPopup = dismissDeleteStreamBlockPopup;

// Wrap default `dismissRelatedLookupPopup`.
window.dismissRelatedLookupPopup = dismissLookupStreamBlockPopup(window.dismissRelatedLookupPopup);
