import React from "react";

import { observer } from "mobx-react"
import { observable, action } from "mobx"
import { httpClient, configurations } from "../init";
import { ITimersFilter, IIndexInfo, ISimpleTimers, ISimpleTimersEx } from "../models/DataModel";
import Dropdown from 'react-bootstrap/Dropdown'
import { DropdownButton, Button, ButtonToolbar, ButtonGroup, Alert, Row } from "react-bootstrap";
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
import { getOptions, registerOptions } from "./BenchmarkView.Options";
import { BenchmarkViewModel, getConfigurationName, trimSha } from "./BenchmarkView.Model";
import { BenchmarkViewChart, DD } from "./BenchmarkView.Chart";
import { Col } from "reactstrap";
import { RenderStats } from "./BenchmarView.Stats";
addHighchartsMore(Highcharts);


(window as any).Color = Color;
(window as any).Highcharts = Highcharts;
const defaultFormat = (i: any) => i.toFixed(2);


const noFormat = i => i;
const flow123dCommitUrl = "https://github.com/flow123d/flow123d/commit/";
const outlierCoef = 0.25;
const maxCommitByDefault = 100;

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
        const value = prop.format(prop.prop(point) || null);
        return `<dt>${prop.title}:</dt> <dd>${value}</dd>`;
    }).join("")
        }
        <dl>
    </div>`
}


const checkOutliers = (item: ISimpleTimersEx) => {
    const j = item as Required<ISimpleTimersEx>;
    const low = j.median - j.low > j.median * outlierCoef;
    const high = j.high - j.median > j.median * outlierCoef;
    return { low, high };
}

interface BenchmarkViewState {
    model: BenchmarkViewModel;
    foo: number;
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

    @observable
    private showTooltip = false;

    @observable
    private commitFilter: string[] = [];

    @observable
    private timerLocked: boolean = false;

    private setTimer: any;

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
        window.addEventListener("keydown", e => this.handleKeyDown(e));
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

                //const { data, outliers } = this.fixData(rawData);
                const data: ISimpleTimersEx[] = rawData.map(
                    i => {
                        const dur = i.durations || [0, 0, 0];
                        const len = dur.length;
                        const int = Math.floor;

                        return {
                            ...i,
                            low: Math.min(...dur),
                            high: Math.max(...dur),
                            median: dur[int(len / 2)],
                            q1: dur[int(len * 0.25)],
                            q3: dur[int(len * 0.75)],
                        }
                    }
                )

                //this.data = data;
                //this.outliers = outliers

                this.model.items = data;
                this.model.ratio = json.ratio;

                this.setState({ foo: Math.random() });
                NotificationApi.success('Data loaded', "", 1000);
            });
    }

    switchConfig(item: IIndexInfo) {
        this.model.configuration = item;
        this.load();
    }

    /*fixData(items: ISimpleTimersEx[]) {
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
    }*/

    @action.bound
    handleKeyDown(e: KeyboardEvent) {
        if (e.key === "Shift") {
            this.showTooltip = !this.showTooltip;
        }
    }

    render() {
        const { commitFilter, model, showBroken } = this;
        const configurationName = getConfigurationName(model.configuration);
        const { size, simple, hideTitle } = this.props;
        const isSmall = size === "small";
        const isSimple = simple === true;
        const data = model.items;

        if (model.items.length === 0) {
            return <SimpleLoader />
        }
        console.log("render");
        return <>

            {!simple &&
                <Row>
                    <ButtonToolbar>
                        <ButtonGroup>
                            <Button variant="dark" onClick={(i) => this.load()}>
                                <FontAwesomeIcon icon={faRedo} />
                            </Button>
                            <DropdownButton id="dropdown-basic-button"
                                title={`${configurationName} [${data.length} commits]`} as={ButtonGroup}>
                                {configurations.map((item, j) =>
                                    <Dropdown.Item
                                        key={getConfigurationName(item)}
                                        onSelect={i => {
                                            this.switchConfig(item);
                                            (this.props as any).history.push(`/benchmarks/${j}`);
                                        }}
                                        active={configurationName === getConfigurationName(item)}
                                    >
                                        {getConfigurationName(item)}
                                    </Dropdown.Item>
                                )}
                            </DropdownButton>
                        </ButtonGroup>
                        <Button onClick={() => this.showBroken = !showBroken}>
                            Toggle broken builds
                    </Button>
                    </ButtonToolbar>
                </Row>
            }
            <Row>
                <Col lg={isSmall ? 12 : 9}>
                    <BenchmarkViewChart
                        commitFilter={commitFilter}
                        hideTitle={hideTitle === true}
                        isSmall={isSmall}
                        model={model}
                        showBroken={showBroken}
                        onClick={(timer) => {
                            if (!this.setTimer) {
                                return;
                            }

                            this.timerLocked = !this.timerLocked;
                            this.setTimer(timer);

                            if (this.timerLocked) {
                                this.commitFilter = [
                                    ...(timer.left || []),
                                    ...(timer.right || []),
                                ]
                            } else {
                                this.commitFilter = [];
                            }
                        }}
                        onHover={(timer) => {
                            if (!this.setTimer) {
                                return;
                            }
                            if (!this.timerLocked) {
                                this.setTimer(timer);
                            }
                        }}
                    />
                </Col>
                {!isSmall &&
                    <Col lg={3}>
                        <RenderStats
                            onInit={setTimer => this.setTimer = setTimer}
                            timers={data}
                        />
                    </Col>}
            </Row>
        </>

        /*
            new Prop("count", "N", i => i.toFixed()),
            new Prop("info.branch", "Branch", noFormat),
            new Prop("info.branches", "Branches", (i: string[]) => filterBranches(i).join(", ")),
            new Prop("welch.pValue", "pValue", (i: number) => i == null ? "" : i.toFixed(3)),
            new Prop("welch.estimatedValue1", "x1", (i: number) => i == null ? "" : i.toFixed(2)),
            new Prop("welch.estimatedValue2", "x2", (i: number) => i == null ? "" : i.toFixed(2)),
            new Prop("welch.radius", "r", (i: number) => i == null ? "" : i),
            new Prop("welch.n1", "n1", (i: number) => i == null ? "" : i),
            new Prop("welch.n2", "n2", (i: number) => i == null ? "" : i),
            new Prop("left", "left", (i: string[]) => i == null ? "" : i.join(', ')),
            new Prop("right", "right", (i: string[]) => i == null ? "" : i.join(', ')),
            new Prop("fooo", " ", (i: any) => "-----------------<br />"),
            "count",
            "low",
            "q1",
            "median",
            "q3",
            "high",
        */

        /*return <>
            {!simple &&
                <ButtonToolbar>
                    <ButtonGroup>
                        <Button variant="dark" onClick={(i) => this.load()}>
                            <FontAwesomeIcon icon={faRedo} />
                        </Button>
                        <DropdownButton id="dropdown-basic-button"
                            title={`${configurationName} [${data.length} commits]`} as={ButtonGroup}>
                            {configurations.map((item, j) =>
                                <Dropdown.Item
                                    key={getConfigurationName(item)}
                                    onSelect={i => {
                                        this.switchConfig(item);
                                        (this.props as any).history.push(`/benchmarks/${j}`);
                                    }}
                                    active={configurationName === getConfigurationName(item)}
                                >
                                    {getConfigurationName(item)}
                                </Dropdown.Item>
                            )}
                        </DropdownButton>
                    </ButtonGroup>
                    <Button onClick={() => this.showBroken = !showBroken}>
                        Toggle broken builds
                    </Button>
                </ButtonToolbar>
            }
            {xLabels.length > 0 &&
                <div className={`${this.showTooltip ? "" : "no-tooltip"}`}>
                <HighchartsReact highcharts={Highcharts} options={options} />

                    {!this.props.simple &&
                        <div>
                            <Alert variant="info">
                                <em>Note</em> By default only the last {maxCommitByDefault} commits are visible,
                                use <strong>Reset zoom</strong> to view all of the commits
                            </Alert>
                            <Alert variant="light">
                                <em>Note</em> If <strong>|max - μ| {'>'} ε/μ</strong>, max is marked as an outlier if the chart
                                in order to simplify the chart, <strong>ε</strong> is currently {outlierCoef * 100}%
                            </Alert>
                        </div>
                    }
                </div>
            }
        </>*/
    }
}