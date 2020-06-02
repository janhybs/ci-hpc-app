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

    private oldCommitSha: string = "";

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
        const { commitFilter, model, showBroken, oldCommitSha } = this;
        const configurationName = getConfigurationName(model.configuration);
        const { size, simple, hideTitle } = this.props;
        const isSmall = size === "small";
        const isSimple = simple === true;
        const data = model.items;
        const detailMode = commitFilter.length > 0;


        const handleClick = (timer: ISimpleTimers) => {
            if (!this.setTimer) {
                return;
            }
            
            const newCommitSha = timer.commit;
            this.setTimer(timer);
            if(detailMode && newCommitSha === oldCommitSha) {
                this.oldCommitSha = "";
                this.commitFilter = [];
            } else {
                this.oldCommitSha = timer.commit;
                this.commitFilter = [
                    ...(timer.left || []),
                    ...(timer.right || []),
                ];
            }
        }

        const handleHover = (timer: ISimpleTimers) => {
            if (!this.setTimer) {
                return;
            }
            
            if (!this.timerLocked) {
                this.setTimer(timer);
            }
        }

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
                        detailCommit={oldCommitSha}
                        onClick={timer => handleClick(timer)}
                        onHover={timer => handleHover(timer)}
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
    }
}