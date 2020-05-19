import React from "react";

import { observer } from "mobx-react"
import { observable } from "mobx"
import { httpClient, configurations } from "../init";
import { ITimersFilter, IIndexInfo, ISimpleTimers } from "../models/DataModel";
import Dropdown from 'react-bootstrap/Dropdown'
import { DropdownButton, Button, ButtonToolbar, ButtonGroup, Alert } from "react-bootstrap";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faRedo } from '@fortawesome/free-solid-svg-icons'
import Color from "color"

import moment from "moment";
import "../styles/chart.css";

import HighchartsReact from 'highcharts-react-official';
import Highcharts from 'highcharts/highstock';
import addHighchartsMore from 'highcharts/highcharts-more';
import { NotificationApi } from "../utils/Notification";
import { SimpleLoader } from "../components/SimpleLoader";
addHighchartsMore(Highcharts);


(window as any).Color = Color;
(window as any).Highcharts = Highcharts;
const defaultFormat = (i: any) => i.toFixed(2);


const noFormat = i => i;
const flow123dCommitUrl = "https://github.com/flow123d/flow123d/commit/";
const outlierCoef = 0.25;
const maxCommitByDefault = 30;

interface IOutlier {
    x: string;
    y: number;
}

const getColor = (point: ISimpleTimers) => {
    return point.isBroken
        ? "gray"
        : (point.welch !== null && point.welch.significant
            ? (point.welch.estimatedValue1 < point.welch.estimatedValue2 ? "green" : "red")
            : null);
}

const filterBranches = (branches: string[]) =>
    branches.filter(i => i != "HEAD");

class Prop {
    constructor(public key: string, public title?: string, public format = defaultFormat) {
        this.title = this.title || this.key;
        this.title = this.title.substr(0, 1).toUpperCase() + this.title.substr(1);
    }
    public prop(o: any) {
        const keys = this.key.split(".");
        let c = o;
        try {
            keys.forEach(i => c = c[i]);
            return c;
        } catch (error) {
            return null;
        }
    }
}

const pointFormatter = (xLabels: string[], point: any, ...props: (Prop | string)[]) => {

    return `<div onclick="window.open('${flow123dCommitUrl}${xLabels[point.x]}', '_blank')">
        <code>
            <a href="${flow123dCommitUrl}${xLabels[point.x]}" target="_blank">
                ${xLabels[point.x].substr(0, 16)}
            </a>
        </code>
        <dl class="boxplot">
            ${props.map(p => {
        const prop: Prop = typeof (p) === "string" ? new Prop(p as string) : p as Prop;
        const value = prop.format(prop.prop(point) || NaN);
        return `<dt>${prop.title}:</dt> <dd>${value}</dd>`;
    }).join("")
        }
        <dl>
    </div>`
}


const checkOutliers = (item: ISimpleTimers) => {
    const j = item as Required<ISimpleTimers>;
    const low = j.median - j.low > j.median * outlierCoef;
    const high = j.high - j.median > j.median * outlierCoef;
    return { low, high };
}

interface BenchmarkViewState {
    model: BenchmarkViewModel;
    foo: number;
}

class BenchmarkViewModel {

    @observable
    public configuration: IIndexInfo = configurations[0] as IIndexInfo;

    @observable
    public items: ISimpleTimers[] = [];

    public get filter(): ITimersFilter {
        return {
            info: this.configuration,
            limit: 5000,
        } as ITimersFilter;
    }
}

export interface BenchmarkViewProps {
    simple?: boolean;
    hideTitle?: boolean;
    hideXTicks?: boolean;
    configuration?: IIndexInfo;
    size?: "big" | "small";

    hideBroken?: boolean
}

@observer
export class BenchmarkView extends React.Component<BenchmarkViewProps, BenchmarkViewState, {}> {

    @observable
    public model = new BenchmarkViewModel()

    private data: any[] = []
    private outliers: IOutlier[] = [];

    @observable
    private ratio: number = NaN;

    @observable
    private showBroken = false;

    constructor(state) {
        super(state);

        const match = (this.props as any).match;
        const index = match ? match.params.index : null;

        if (this.props.configuration != null) {
            this.model.configuration = this.props.configuration
        } else if (index != null) {
            this.model.configuration = configurations[index] as IIndexInfo;
        }
        this.load();
    }

    load() {
        httpClient.fetch<ISimpleTimers[]>("timers/list", this.model.filter)
            .then((json: any) => {

                let rawData = json.data as ISimpleTimers[];
                this.ratio = json.ratio;

                if (this.props.hideBroken === true) {
                    rawData = rawData
                        .filter(i => i.isBroken === false);
                }

                /*const sortedData = rawData.sort((b, a) => {
                    const dateB = b.info ? new Date(b.info.date as any).getTime() : 0;
                    const dateA = a.info ? new Date(a.info.date as any).getTime() : 0;
                    return dateB - dateA;
                });*/

                const { data, outliers } = this.fixData(rawData);

                this.data = data;
                this.outliers = outliers
                // this.setState({foo: Math.random()});

                this.model.items = data;

                NotificationApi.success('Data loaded', "", 1000);
            });
    }

    switchConfig(item: IIndexInfo) {
        this.model.configuration = item;
        this.load();
    }

    configurationName(item: IIndexInfo) {
        return `${item.test} ${item.benchmark} ${item.mesh}`;
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
        const { data: dataRaw, outliers } = this;
        const data = this.model.items
            .filter(i => !i.isBroken || this.showBroken) as any[];

        const itemsRaw = data as ISimpleTimers[];

        const commits = new Map(itemsRaw.map((c, i) => [c.commit, i]));
        const commitInfo = new Map(itemsRaw.map(c => [c.commit, c.info]));
        const xLabels = [...commits.keys()] as string[];

        const isSmall = this.props.size === "small";
        const boxplotVisible = !isSmall,
            medianVisible = isSmall,
            outliersVisible = false,
            defaultZoom = !isSmall;

        if (data.length === 0) {
            return <SimpleLoader />
        }

        const title = this.props.hideTitle ? ""
            : `${configurationName}<br /><small>(${(this.ratio * 100).toFixed(2)} % working)</small>`;

        return <>
            {!this.props.simple &&
                <ButtonToolbar>
                    <ButtonGroup>
                        <Button variant="dark" onClick={(i) => this.load()}>
                            <FontAwesomeIcon icon={faRedo} />
                        </Button>
                        <DropdownButton id="dropdown-basic-button"
                            title={`${configurationName} [${data.length} commits]`} as={ButtonGroup}>
                            {configurations.map(item =>
                                <Dropdown.Item
                                    key={this.configurationName(item)}
                                    onSelect={i => this.switchConfig(item)}
                                    active={configurationName === this.configurationName(item)}
                                >
                                    {this.configurationName(item)}
                                </Dropdown.Item>
                            )}
                        </DropdownButton>
                    </ButtonGroup>
                    <Button onClick={() => this.showBroken = !this.showBroken}>
                        Toggle broken builds
                    </Button>
                </ButtonToolbar>
            }
            {xLabels.length > 0 &&
                <div>
                    <HighchartsReact highcharts={Highcharts} options={{
                        title: {
                            text: title,
                        },
                        plotOptions: {
                            series: {
                                turboThreshold: 0,
                                animation: isSmall ? false : {
                                    duration: 200,
                                },
                            }
                        },
                        credits: {
                            enabled: false
                        },
                        legend: {
                            enabled: !isSmall,
                        },
                        chart: {
                            zoomType: "x",
                            height: isSmall ? "256" : "700",
                            events: {
                                load: function (ev) {
                                    if (defaultZoom) {
                                        const chart = this as any;
                                        chart.xAxis[0].setExtremes(
                                            chart.series[0].xData.length - maxCommitByDefault,
                                            chart.series[0].xData.length
                                        );
                                        chart.showResetZoom();
                                    }
                                },
                            }
                        },
                        yAxis: {
                            title: {
                                text: null,
                            },
                        },
                        xAxis: {
                            title: {
                                text: null,
                            },
                            tickInterval: 1,
                            labels: {
                                enabled: !this.props.hideXTicks,
                                style: {
                                    fontSize: "9px"
                                },
                                formatter: function () {
                                    try {
                                        const info = commitInfo.get(xLabels[this.value]);

                                        return !info ? xLabels[this.value].substr(0, 8) :
                                            `${moment(info.date as any).fromNow(true)} - ${info.branch || info.branches}`
                                    } catch (error) {
                                        return "";
                                    }
                                }
                            }
                        },
                        tooltip: {
                            useHTML: true,
                            snap: 0,
                        },
                        series: [
                            {
                                type: "area",
                                name: "Median",
                                visible: medianVisible,
                                stickyTracking: medianVisible,
                                data: data.map(i => {
                                    return {
                                        y: i.median as number,
                                        x: commits.get(i.commit),
                                        color: getColor(i as ISimpleTimers)
                                    } as any;
                                }),
                                enableMouseTracking: medianVisible,
                                lineWidth: 1,
                                dashStyle: isSmall ? "Solid" : "ShortDot",
                                marker: {
                                    enabled: isSmall,
                                    radius: 4,
                                },
                                fillColor: {
                                    linearGradient: {
                                        x1: 0,
                                        y1: 0,
                                        x2: 0,
                                        y2: 1
                                    },
                                    stops: [
                                        [0, Color((Highcharts as any).getOptions().colors[0]).alpha(0.3).toString()],
                                        [1, Color((Highcharts as any).getOptions().colors[0]).alpha(0.0).toString()]
                                    ]
                                },
                                tooltip: {
                                    headerFormat: "",
                                    pointFormatter: function () {
                                        return pointFormatter(xLabels, this, new Prop("y", "Median"));
                                    }
                                }
                            },
                            {
                                type: "boxplot",
                                name: "Boxplot",
                                visible: boxplotVisible,
                                stickyTracking: false,
                                color: (Highcharts as any).getOptions().colors[0],
                                tooltip: {
                                    headerFormat: "",
                                    pointFormatter: function () {
                                        return pointFormatter(xLabels, this,
                                            new Prop("count", "N", i => i.toFixed()),
                                            new Prop("info.branch", "Branch", noFormat),
                                            new Prop("info.branches", "Branches", (i: string[]) => filterBranches(i).join(", ")),
                                            new Prop("welch.estimatedValue1", "x1", (i: number) => i == null ? "" : i.toFixed(2)),
                                            new Prop("welch.estimatedValue2", "x2", (i: number) => i == null ? "" : i.toFixed(2)),
                                            new Prop("welch.radius", "r", (i: number) => i == null ? "" : i),
                                            new Prop("welch.n1", "n1", (i: number) => i == null ? "" : i),
                                            new Prop("welch.n2", "n2", (i: number) => i == null ? "" : i),
                                            new Prop("fooo", " ", (i: any) => "<br />"),
                                            "count",
                                            "low",
                                            "q1",
                                            "median",
                                            "q3",
                                            "high",
                                        );
                                    }
                                },
                                data: data.map(i => {
                                    return {
                                        ...i,
                                        x: commits.get(i.commit),
                                        color: getColor(i as ISimpleTimers)
                                    };
                                })
                            },
                            {
                                type: "scatter",
                                name: "Outliers",
                                visible: outliersVisible,
                                stickyTracking: false,
                                color: Color((Highcharts as any).getOptions().colors[0]).darken(0.5).hex(),
                                data: outliers.map(i => {
                                    return { y: i.y, x: commits.get(i.x) };
                                }),
                                tooltip: {
                                    headerFormat: "",
                                    pointFormatter: function () {
                                        return pointFormatter(xLabels, this, new Prop("y", "Value"));
                                    }
                                },
                            },
                        ]
                    }} />

                    {!this.props.simple &&
                        <div>
                            <Alert variant="info">
                                <em>Note</em> By default only the last {maxCommitByDefault} commits are visible,
                                use <strong>Reset zoom</strong> to view all of the commits
                            </Alert>
                            <Alert variant="light">
                                <em>Note</em> If <strong>|max - μ| > ε/μ</strong>, max is marked as an outlier if the chart
                                in order to simplify the chart, <strong>ε</strong> is currently {outlierCoef * 100}%
                            </Alert>
                        </div>
                    }
                </div>
            }
        </>
    }
}