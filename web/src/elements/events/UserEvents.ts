import { t } from "@lingui/macro";

import { html, TemplateResult } from "lit";
import { customElement, property } from "lit/decorators";

import { Event, EventsApi } from "@goauthentik/api";

import { AKResponse } from "../../api/Client";
import { DEFAULT_CONFIG } from "../../api/Config";
import { EventWithContext } from "../../api/Events";
import { uiConfig } from "../../common/config";
import "../../pages/events/EventInfo";
import "../Tabs";
import "../buttons/Dropdown";
import "../buttons/ModalButton";
import "../buttons/SpinnerButton";
import { Table, TableColumn } from "../table/Table";

@customElement("ak-events-user")
export class ObjectChangelog extends Table<Event> {
    expandable = true;

    @property()
    order = "-created";

    @property()
    targetUser!: string;

    async apiEndpoint(page: number): Promise<AKResponse<Event>> {
        return new EventsApi(DEFAULT_CONFIG).eventsEventsList({
            page: page,
            ordering: this.order,
            pageSize: (await uiConfig()).pagination.perPage / 2,
            username: this.targetUser,
        });
    }

    columns(): TableColumn[] {
        return [
            new TableColumn(t`Action`, "action"),
            new TableColumn(t`User`, "enabled"),
            new TableColumn(t`Creation Date`, "created"),
            new TableColumn(t`Client IP`, "client_ip"),
        ];
    }

    row(item: EventWithContext): TemplateResult[] {
        return [
            html`${item.action}`,
            html`<div>${item.user?.username}</div>
                ${item.user.on_behalf_of
                    ? html`<small> ${t`On behalf of ${item.user.on_behalf_of.username}`} </small>`
                    : html``}`,
            html`<span>${item.created?.toLocaleString()}</span>`,
            html`<span>${item.clientIp || t`-`}</span>`,
        ];
    }

    renderExpanded(item: Event): TemplateResult {
        return html` <td role="cell" colspan="4">
                <div class="pf-c-table__expandable-row-content">
                    <ak-event-info .event=${item as EventWithContext}></ak-event-info>
                </div>
            </td>
            <td></td>
            <td></td>
            <td></td>`;
    }

    renderEmpty(): TemplateResult {
        return super.renderEmpty(html`<ak-empty-state header=${t`No Events found.`}>
            <div slot="body">${t`No matching events could be found.`}</div>
        </ak-empty-state>`);
    }
}
