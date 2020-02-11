import React from "react";
import { observer } from "mobx-react"
import { observable, action } from "mobx"
import { httpClient } from "../init";
import { IColScheduler, ITimersFilter, IIndexInfo, IColTimers, ISimpleTimer } from "../models/DataModel";
import Dropdown from 'react-bootstrap/Dropdown'
import Moment from 'react-moment';
import { DropdownButton } from "react-bootstrap";


const configurations: IIndexInfo[] =  [
    {
        project: "flow123d",
        test: "01_square_regular_grid",
        benchmark: "transport.yaml",
        mesh: "1_15662_el",
        cpus: 1
    },
    {
        project: "flow123d",
        test: "01_square_regular_grid",
        benchmark: "transport.yaml",
        mesh: "2_31498_el",
        cpus: 1
    }
];

interface BenchmarkViewState {
    model: BenchmarkViewModel;
}

class BenchmarkViewModel {

    @observable
    public configuration: IIndexInfo = configurations[0];

    @observable
    public items: ISimpleTimer[] = [];

    public get filter(): ITimersFilter {
        return {
            info: this.configuration,
            limit: 500,
        };
    }
}

@observer
export class BenchmarkView extends React.Component<{}, BenchmarkViewState, {}> {

    @observable
    public model = new BenchmarkViewModel()

    constructor(state) {
        super(state);
        this.load();
    }

    load() {
        httpClient.fetch<ISimpleTimer[]>("timers/list", this.model.filter)
            .then(data => {
                this.model.items = data;
            });
    }

    public switchConfig(item: IIndexInfo) {
        this.model.configuration = item;
        this.load();
    }

    public configurationName(item: IIndexInfo) {
        return `${item.cpus} x ${item.test} ${item.benchmark} ${item.mesh}`;
    }

    render() {
        const configurationName = this.configurationName(this.model.configuration);
        return <>
        <DropdownButton id="dropdown-basic-button" title={configurationName}>
            {configurations.map(item => 
                <Dropdown.Item key={this.configurationName(item)} onSelect={i => this.switchConfig(item)}>
                    {this.configurationName(item)}
                </Dropdown.Item>
            )}
        </DropdownButton>
            <span>{this.model.items.length}</span>
        </>
    }
}