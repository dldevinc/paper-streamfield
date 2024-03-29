/* global gettext */
/* global Sortable */
/* global XClass */
import { v4 as uuid4, validate as uuid_validate } from "uuid";

import "./widget.scss";

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
        buttons: "stream-field__buttons",
        sortableHandler: "stream-field__sortable-handler",
        visibilitySwitch: "stream-field__visibility-switch",
        changeBlockButton: "stream-field__change-btn",
        deleteBlockButton: "stream-field__delete-btn",
        dropdownItemButton: "stream-field__dropdown-item" // create or lookup block
    };

    constructor(element) {
        this.field = element;
        this.control = this.field.querySelector(`.${this.CSS.control}`);
        this.blocks = this.field.querySelector(`.${this.CSS.blocks}`);
        this.buttons = this.field.querySelector(`.${this.CSS.buttons}`);

        this._sortable = this._initSortable();
        this._addListeners();
        this._updateBlockMap();

        this.wrapPreloader(Promise.all([this.updateBlocks(), this.updateButtons()]));
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
        return data;
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
        return Array.from(this.blocks.querySelectorAll(`.${this.CSS.block}`));
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
            if (typeof uuid === "string" && uuid_validate(uuid)) {
                // Add visibility field for data created
                // with `paper-streamfield` <= 0.6.0
                if (!record.hasOwnProperty("visible")) {
                    record.visible = true;
                }

                return (result[uuid] = record);
            } else {
                hasBadBlocks = true;
                uuid = uuid4();
                return (result[uuid] = { uuid: uuid });
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
        this.field.addEventListener("change", event => {
            const visibilitySwitch = event.target.closest(`.${this.CSS.visibilitySwitch}`);
            if (visibilitySwitch) {
                visibilitySwitch.disabled = true;
                const blockElement = visibilitySwitch.closest(`.${this.CSS.block}`);
                const uuid = blockElement.dataset.uuid;
                const block = this.getBlockByUUID(uuid);
                const input = visibilitySwitch.querySelector("input");
                const state = Boolean(input && input.checked);
                block.visible = state;
                blockElement.classList.toggle("stream-field--hidden", !state);
                this.save();
            }
        });

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
                                this.wrapPreloader(this.updateBlocks());
                            }
                        }
                    ],
                    onInit: function () {
                        this.show();
                    },
                    onDestroy: function () {
                        deleteButton.disabled = false;
                    }
                });
            }

            const changeButton = event.target.closest(`.${this.CSS.changeBlockButton}`);
            if (changeButton) {
                event.preventDefault();
                const jQueryEvent = $.Event("django:show-related", { href: changeButton.href });
                $(changeButton).trigger(jQueryEvent);
                if (!jQueryEvent.isDefaultPrevented()) {
                    showStreamBlockPopup(changeButton);
                }
            }

            const dropdownItem = event.target.closest(`.${this.CSS.dropdownItemButton}`);
            if (dropdownItem) {
                event.preventDefault();
                const jQueryEvent = $.Event("django:show-related", { href: dropdownItem.href });
                $(dropdownItem).trigger(jQueryEvent);
                if (!jQueryEvent.isDefaultPrevented()) {
                    showStreamBlockPopup(dropdownItem);
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

    /**
     * @param {Promise} promise
     * @returns {Promise}
     */
    wrapPreloader(promise) {
        this.status = this.STATUS.LOADING;
        return promise.finally(() => {
            this.status = this.STATUS.READY;
        });
    }

    updateBlocks() {
        return this.renderStream({
            allowedModels: this.allowedModels,
            value: this.value
        });
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
        })
            .then(response => {
                if (!response.ok) {
                    throw `${response.status} ${response.statusText}`;
                }
                return response.json();
            })
            .then(response => {
                this.blocks.innerHTML = response.blocks;
            })
            .catch(reason => {
                if (reason instanceof Error) {
                    // JS-ошибки дублируем в консоль
                    console.error(reason);
                }
                modals.showErrors(reason);
            });
    }

    updateButtons() {
        return this.renderButtons({
            field_id: this.control.id,
            allowedModels: this.allowedModels
        });
    }

    renderButtons(data) {
        const renderUrl = this.field.dataset.renderButtonsUrl;
        return fetch(renderUrl, {
            method: "POST",
            mode: "same-origin",
            cache: "no-store",
            headers: {
                "Content-Type": "application/json;charset=utf-8"
            },
            body: JSON.stringify(data)
        })
            .then(response => {
                if (!response.ok) {
                    throw `${response.status} ${response.statusText}`;
                }
                return response.json();
            })
            .then(response => {
                this.buttons.innerHTML = response.buttons;
            });
    }
}

XClass.register("paper-streamfield", {
    init: function (element) {
        element._streamField = new StreamField(element, this);
    },
    destroy: function (element) {
        if (element._streamField) {
            element._streamField.destroy();
            delete element._streamField;
        }
    }
});

/**
 * @param {HTMLElement} triggeringLink
 */
function showStreamBlockPopup(triggeringLink) {
    return popupUtils.showAdminPopup(triggeringLink, /^$/, true);
}

/**
 * @param {Function} originalFunc
 */
function dismissAddStreamBlockPopup(originalFunc) {
    return function(win, newId, newRepr) {
        const name = popupUtils.removePopupIndex(win.name);
        const match = /^streamfield:add_(?<elementId>.+)--(?<blockModel>.+\..+)$/.exec(name);
        if (match) {
            const control = document.getElementById(match.groups.elementId);
            if (!control) {
                console.error(`Control not found: #${match.groups.elementId}`);
                popupUtils.removeRelatedWindow(win);
                win.close();
            }

            const field = control.closest(".stream-field");
            const streamField = field && field._streamField;

            streamField._appendBlock({
                model: match.groups.blockModel,
                pk: newId,
                uuid: uuid4(),
                visible: true
            });

            streamField.wrapPreloader(streamField.updateBlocks());

            popupUtils.removeRelatedWindow(win);
            win.close();
        } else {
            originalFunc.apply(window, arguments);
        }
    }
}

/**
 * @param {Function} originalFunc
 */
function dismissChangeStreamBlockPopup(originalFunc) {
    return function(win, objId, newRepr, newId) {
        const name = popupUtils.removePopupIndex(win.name);
        const match = /^streamfield:change_block_(?<uuid>.+)$/.exec(name);
        if (match) {
            const block = document.querySelector(`.stream-field__block[data-uuid="${match.groups.uuid}"]`);
            if (!block) {
                console.error(`Block not found: ${match.groups.uuid}`);
                popupUtils.removeRelatedWindow(win);
                win.close();
            }

            const fieldWrapper = block && block.closest(".paper-widget");
            const field = fieldWrapper && fieldWrapper.firstElementChild;
            const instance = field && field._streamField;

            instance.updateBlocks();

            popupUtils.removeRelatedWindow(win);
            win.close();
        } else {
            originalFunc.apply(window, arguments);
        }
    }
}

/**
 * @param {Function} originalFunc
 */
function dismissDeleteStreamBlockPopup(originalFunc) {
    return function(win, objId) {
        const name = popupUtils.removePopupIndex(win.name);
        const match = /^streamfield:lookup_(?<elementId>.+)--(?<blockModel>.+\..+)$/.exec(name);
        if (match) {
            win.history.go(-win.history.length + 1);
        } else {
            originalFunc.apply(window, arguments);
        }
    }
}

/**
 * Обёртка над Django-обработчиком `window.dismissRelatedLookupPopup`.
 * @param {Function} originalFunc
 */
function dismissLookupStreamBlockPopup(originalFunc) {
    return function(win, chosenId) {
        const name = popupUtils.removePopupIndex(win.name);
        const match = /^streamfield:lookup_(?<elementId>.+)--(?<blockModel>.+\..+)$/.exec(name);
        if (match) {
            const control = document.getElementById(match.groups.elementId);
            if (!control) {
                console.error(`Control not found: #${match.groups.elementId}`);
                popupUtils.removeRelatedWindow(win);
                win.close();
            }

            const field = control.closest(".stream-field");
            const streamField = field && field._streamField;

            streamField._appendBlock({
                model: match.groups.blockModel,
                pk: chosenId,
                uuid: uuid4(),
                visible: true
            });

            streamField.wrapPreloader(streamField.updateBlocks());

            popupUtils.removeRelatedWindow(win);
            win.close();
        } else {
            originalFunc.apply(window, arguments);
        }
    }
}

// Wrap default callbacks.
window.dismissRelatedLookupPopup = dismissLookupStreamBlockPopup(window.dismissRelatedLookupPopup);
window.dismissAddRelatedObjectPopup = dismissAddStreamBlockPopup(window.dismissAddRelatedObjectPopup);
window.dismissChangeRelatedObjectPopup = dismissChangeStreamBlockPopup(window.dismissChangeRelatedObjectPopup);
window.dismissDeleteRelatedObjectPopup = dismissDeleteStreamBlockPopup(window.dismissDeleteRelatedObjectPopup);
