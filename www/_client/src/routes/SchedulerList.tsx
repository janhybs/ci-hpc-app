import React from "react";
import { observer } from "mobx-react"
import { observable, action } from "mobx"
import { httpClient } from "../init";
import { IColScheduler, ISchedulerFilter } from "../models/DataModel";
import Dropdown from 'react-bootstrap/Dropdown'
import Moment from 'react-moment';
import { DropdownButton, Alert, Container } from "react-bootstrap";

const flow123dCommitUrl = "https://github.com/flow123d/flow123d/commit/";
enum ColSchedulerStatus {
    NotProcessed = 10,
    Running = 20,
    Processed = 30
}

const limitValue = 15;


const schedulerStatuses = [
    { name: "In Queue", value: ColSchedulerStatus.NotProcessed },
    { name: "Processed", value: ColSchedulerStatus.Processed },
    { name: "Running", value: ColSchedulerStatus.Running },
];

interface SchedulerListState {
    model: SchedulerListModel;
}

class SchedulerListModel {
    @observable
    public items: IColScheduler[] = [];

    @observable
    public filter: ISchedulerFilter = {
        limit: 1000,
        status: ColSchedulerStatus.NotProcessed as any,
    }
}

@observer
export class SchedulerList extends React.Component<{}, SchedulerListState, {}> {

    @observable
    public model = new SchedulerListModel()

    constructor(state) {
        super(state);
        this.load();
    }

    load() {
        httpClient.fetch<IColScheduler[]>("scheduler/list", this.model.filter)
            .then(data => {
                this.model.items = data;
            });
    }

    renderStatus(scheduler: Required<IColScheduler>) {
        const index = scheduler.index;
        const date = new Date(scheduler.id.timestamp ? scheduler.id.timestamp * 1000 : 0);

        return <li key={scheduler.objectId}>
            <code>
                <a href={flow123dCommitUrl + index.commit} target="_blank">
                    {index.commitShort} [{index.branch}]
                </a> - {this.getStatusName(scheduler.status)}
            </code>
            <div>submitted <Moment date={date} fromNow ago /> ago</div>
        </li>
    }

    switchStatus(status: any) {
        this.model.filter = {
            status: status,
            limit: this.model.filter.limit,
        };
        this.load();
    }

    getStatusName(status: any) {
        const statusName = schedulerStatuses.find(i => i.value === status);
        return statusName ? statusName.name : "";
    }


    render() {
        const items = this.model.items;

        return <Container>
            <DropdownButton id="dropdown-basic-button" title={`${this.getStatusName(this.model.filter.status)} [${this.model.items.length}]`}>
                {schedulerStatuses.map(item =>
                    <Dropdown.Item key={item.value} onSelect={i => this.switchStatus(item.value)}>{item.name}</Dropdown.Item>
                )}
            </DropdownButton>
            <div>
                <ul>
                    {items
                        .filter((i, j) => i.index != null && j < limitValue)
                        .map(i => this.renderStatus(i as Required<IColScheduler>))
                    }
                    {items.length > limitValue &&
                        <Alert variant="warning">
                            {items.length - limitValue} items are hidden
                    </Alert>
                    }
                </ul>
            </div>
        </Container>
    }
}