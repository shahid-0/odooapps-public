/** @odoo-module **/
import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { Component, useState, onWillStart } from "@odoo/owl";
import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { Dialog } from "@web/core/dialog/dialog";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";

/* -------------------------------------------------------------------------- */
/*                            Add Note Modal (ORM)                            */
/* -------------------------------------------------------------------------- */
class AddNoteModal extends Component {
    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.state = useState({ noteText: "" });
    }

    cancel() {
        this.env.services.dialog.close();
    }

    async saveNote() {
        const text = this.state.noteText.trim();
        if (!text) return;

        try {
            const id = await this.orm.create("sticky.note", [{
                name: text.split("\n")[0] || "New Note",
                text,
            }]);

            // read created record
            const [newNote] = await this.orm.read("sticky.note", [id?.[0]], ["id", "name", "text"]);

            // notify user
            this.notification.add("Note created successfully!", { type: "success" });

            // close modal and return new note to parent if needed
            this.props.close({ newNote });
        } catch (error) {
            console.error("Error creating note:", error);
            this.notification.add("Failed to create note", { type: "danger" });
        }
    }
}
AddNoteModal.template = "add_note_modal";
AddNoteModal.components = { Dialog };

/* -------------------------------------------------------------------------- */
/*                           View Notes Modal (ORM)                           */
/* -------------------------------------------------------------------------- */
class ViewNotesModal extends Component {
    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.dialog = useService("dialog");

        this.state = useState({
            notes: [],
            editingId: null,
            editText: "",
        });

        onWillStart(async () => {
            this.state.notes = await this.orm.searchRead("sticky.note", [], ["id", "name", "text"]);
        });
    }

    cancel() {
        this.props.close();
    }

    /* ---------------------------- DELETE NOTE ---------------------------- */
    async deleteNote(ev) {
        const id = Number(ev.currentTarget.dataset.id);
        try {
            this.dialog.add(ConfirmationDialog, {
                title: _t("Delete Note"),
                body: _t("Are you sure you want to delete that record?"),
                confirmClass: "btn-primary",
                confirm: async () => {
                    await this.orm.unlink("sticky.note", [id]);
                    this.state.notes = this.state.notes.filter((n) => n.id !== id);
                    this.notification.add("Note deleted", { type: "success" });
                },
                confirmLabel: _t("Yes"),
                cancelLabel: _t("No"),
                cancel: () => { },
            });
        } catch (error) {
            this.notification.add("Error deleting note", { type: "danger" });
            console.error(error);
        }
    }

    /* ----------------------------- EDIT NOTE ----------------------------- */
    startEdit(ev) {
        const id = Number(ev.currentTarget.dataset.id);
        const note = this.state.notes.find((n) => n.id === id);
        if (note) {
            this.state.editingId = id;
            this.state.editText = note.text;
        }
    }

    onKeydownEdit(ev) {
        if (ev.key === "Enter" && ev.ctrlKey) {
            this.saveEdit();
        } else if (ev.key === "Escape") {
            this.cancelEdit();
        }
    }

    async saveEdit() {
        const id = this.state.editingId;
        if (!id) return;
        const text = this.state.editText.trim();
        if (!text) return;

        try {
            await this.orm.write("sticky.note", [id], { text });
            const note = this.state.notes.find((n) => n.id === id);
            if (note) note.text = text;

            this.state.editingId = null;
            this.state.editText = "";
            this.notification.add("Note updated", { type: "success" });
        } catch (error) {
            this.notification.add("Failed to update note", { type: "danger" });
            console.error(error);
        }
    }

    cancelEdit() {
        this.state.editingId = null;
        this.state.editText = "";
    }
}
ViewNotesModal.template = "view_notes_modal";
ViewNotesModal.components = { Dialog };

/* -------------------------------------------------------------------------- */
/*                           Systray Dropdown Entry                           */
/* -------------------------------------------------------------------------- */
class SystrayDropdown extends Component {
    setup() {
        this.dialog = useService("dialog");
        this.orm = useService("orm");
        this.notification = useService("notification");

        this.state = useState({
            notes: [],
        });

        onWillStart(async () => {
            this.state.notes = await this.orm.searchRead("sticky.note", [], ["id", "name", "text"]);
        });
    }

    /* ---------------------------- OPEN MODALS ---------------------------- */
    openAddNoteModal() {
        this.dialog.add(AddNoteModal, {
            close: async (result) => {
                if (result && result.newNote) {
                    this.state.notes.unshift(result.newNote);
                }
            },
        });
    }

    openViewNotesModal() {
        this.dialog.add(ViewNotesModal);
    }
}
SystrayDropdown.template = "systray_dropdown";
SystrayDropdown.components = { Dropdown, DropdownItem };

export const systrayItem = { Component: SystrayDropdown };
registry.category("systray").add("SystrayDropdown", systrayItem, { sequence: 1 });
