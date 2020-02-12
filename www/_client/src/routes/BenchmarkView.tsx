import React from "react";
import { NotificationManager } from 'react-notifications';

import { observer } from "mobx-react"
import { observable } from "mobx"
import { httpClient } from "../init";
import { ITimersFilter, IIndexInfo, ISimpleTimers } from "../models/DataModel";
import Dropdown from 'react-bootstrap/Dropdown'
import { DropdownButton, Button, ButtonToolbar, ButtonGroup } from "react-bootstrap";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faRedo } from '@fortawesome/free-solid-svg-icons'

import "../styles/chart.css";

// import Highcharts from 'highcharts';
import HighchartsReact from 'highcharts-react-official';
import Highcharts from 'highcharts/highstock';
// import HighchartMore from 'highcharts/highcharts-more';
// HighchartMore(ReactHighchart.Highcharts);
import addHighchartsMore from 'highcharts/highcharts-more';
addHighchartsMore(Highcharts);




const flow123dCommitUrl = "https://github.com/flow123d/flow123d/commit/";
const outlierCoef = 0.5;

interface IOutlier {
    x?: string;
    y?: number;
}

interface IProp {
    [key: string]: string
}

const pointFormatter = (xLabels: string[], point: any, ...props: IProp[]) => {

    return `<code>
        <a href="${flow123dCommitUrl}${xLabels[point.x]}" target="_blank">
            ${xLabels[point.x].substr(0, 8)}
        </a>
    </code>
    <dl class="boxplot">
        ${props.map(p => `<dt>${Object.keys(p)[0]}:</dt><dd>${point[Object.values(p)[0]].toFixed(2)}</dd>`).join("")}
    <dl>`;
}


const configurations: IIndexInfo[] = [
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

const checkOutliers = (item: ISimpleTimers) => {
    const j = item as Required<ISimpleTimers>;
    const low = j.median - j.low > j.median * outlierCoef;
    const high = j.high - j.median > j.median * outlierCoef;
    return { low, high };
}

interface BenchmarkViewState {
    model: BenchmarkViewModel;
}

class BenchmarkViewModel {

    @observable
    public configuration: IIndexInfo = configurations[0];

    @observable
    public items: ISimpleTimers[] = [];

    public get filter(): ITimersFilter {
        return {
            info: this.configuration,
            limit: 500,
        };
    }
}

export interface BenchmarkViewProps {
    simple?: boolean;
    configuration?: IIndexInfo;
    size?: "big" | "small";
}

@observer
export class BenchmarkView extends React.Component<BenchmarkViewProps, BenchmarkViewState, {}> {

    @observable
    public model = new BenchmarkViewModel()

    constructor(state) {
        super(state);
        if(this.props.configuration != null) {
            this.model.configuration = this.props.configuration
        }
        this.load();
    }

    load() {
        httpClient.fetch<ISimpleTimers[]>("timers/list", this.model.filter)
            .then((data: ISimpleTimers[]) => {
                this.model.items = data;
                NotificationManager.success('Data loaded', null, 1000);
            });
    }

    switchConfig(item: IIndexInfo) {
        this.model.configuration = item;
        this.load();
    }

    configurationName(item: IIndexInfo) {
        return `${item.cpus} x ${item.test} ${item.benchmark} ${item.mesh}`;
    }

    fixData(items: ISimpleTimers[]) {
        let data: any[] = [];
        let outliers: IOutlier[] = [];

        items.forEach(item => {
            const { low, high } = checkOutliers(item);
            let i = item as any;
            if (low) {
                outliers.push({ x: i.commit, y: i.low });
                i.low = item.q1;
            }
            if (high) {
                outliers.push({ x: i.commit, y: i.high });
                i.high = item.q3;
            }
            data.push(i);
        });

        return { data, outliers };
    }

    render() {
        const configurationName = this.configurationName(this.model.configuration);
        const commits = new Map(this.model.items.map((c, i) => [c.commit, i]));
        const xLabels = [...commits.keys()] as string[];

        const { data, outliers } = this.fixData(this.model.items);


        return <>
        {!this.props.simple &&
                <ButtonToolbar>
                    <ButtonGroup>
                        <Button variant="dark" onClick={(i) => this.load()}>
                            <FontAwesomeIcon icon={faRedo} />
                        </Button>
                        <DropdownButton id="dropdown-basic-button" title={configurationName} as={ButtonGroup}>
                            {configurations.map(item =>
                                <Dropdown.Item key={this.configurationName(item)} onSelect={i => this.switchConfig(item)}>
                                    {this.configurationName(item)}
                                </Dropdown.Item>
                            )}
                        </DropdownButton>
                    </ButtonGroup>
                </ButtonToolbar>
            }
            <div>
                <HighchartsReact highcharts={Highcharts} options={{
                    title: {
                        text: configurationName,
                    },
                    chart: {
                        zoomType: "x",
                        width: this.props.size == "small" ? 600 : null,
                    },
                    yAxis: {
                        crosshair: {
                            snap: false,
                            color: "#00000033",
                            dashStyle: "LongDash",
                        }
                    },
                    xAxis: {
                        crosshair: {
                            snap: false,
                            color: "#00000033",
                            dashStyle: "LongDash",
                        },
                        tickInterval: 1,
                        labels: {
                            enabled: true,
                            formatter: function () {
                                return xLabels[this.value].substr(0, 8);
                            }
                        }
                    },
                    tooltip: {
                        useHTML: true,
                    },
                    series: [
                        {
                            type: "line",
                            name: "Median",
                            data: data.map(i => i.median as number),
                            tooltip: {
                                headerFormat: "",
                                pointFormatter: function () {
                                    return pointFormatter(xLabels, this, { "median": "y" });
                                }
                            },
                        },
                        {
                            type: "boxplot",
                            name: "Boxplot",
                            color: (Highcharts as any).getOptions().colors[0],
                            tooltip: {
                                headerFormat: "",
                                pointFormatter: function () {
                                    return pointFormatter(xLabels, this,
                                        { "Low": "low" },
                                        { "Q1": "q1" },
                                        { "Median": "median" },
                                        { "Q3": "q3" },
                                        { "High": "high" },
                                    );
                                }
                            },
                            data: data.map(i => {
                                return { ...i, x: commits.get(i.commit) };
                            })
                        },
                        {
                            type: "scatter",
                            color: (Highcharts as any).getOptions().colors[0],
                            name: "Outliers",
                            visible: false,
                            data: outliers.map(i => {
                                return { y: i.y, x: commits.get(i.x) };
                            }),
                            tooltip: {
                                headerFormat: "",
                                pointFormatter: function () {
                                    return pointFormatter(xLabels, this, { "value": "y" });
                                }
                            },
                        },
                    ]
                }} />
            </div>
        </>
    }
}