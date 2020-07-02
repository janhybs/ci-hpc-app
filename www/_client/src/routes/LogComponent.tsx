import React from "react";
import { httpClient } from "../init";
import { ICommitRun } from "../models/DataModel";
import { Row, Col, ToggleButton, ToggleButtonGroup } from "react-bootstrap";
import Moment from "react-moment";


interface ILogFilter {
    showBroken: boolean;
    showStable: boolean;
    showNotExecuted: boolean;
    showCompilation: boolean;
    showTests: boolean;
}


const Msg = (props) => {
    const {variant, ...rest} = props;
    return <div className={`alert-${variant} p-1`} {...rest} />
}

const RenderCommitRun = (item: ICommitRun) => {
    const broken = item.runs.filter(i => i.isBroken);
    const stable = item.runs.filter(i => !i.isBroken);

    return <Col className="p-0" sm={6} md={6} xl={3} key={item.commit.commit}>
        <div className="card p-1 m-1">
            <code className="small">{item.commit.commit}</code>
            <code className="tiny">{item.commit.message}</code>
            
            <Msg variant="secondary">
                <span className="number">
                    <Moment date={item.commit.authoredDatetime} format="DD/MM YYYY " />
                    (<Moment date={item.commit.authoredDatetime} fromNow />)
                </span>
            </Msg>

            <div>
                {item.runs.length == 0 && <Msg variant="warning">No builds yet</Msg>}
                {broken.length > 0 && <Msg variant="danger">{broken.length} broken builds</Msg>}
                {stable.length > 0 && <Msg variant="success">{stable.length} stable builds</Msg>}
            </div>
        </div>
    </Col>
}

export const GetLastBuild = (props: any) => {
    const [items, setItems] = React.useState<ICommitRun[]>([]);
    const [filter, setFilter] = React.useState<ILogFilter>({
        showBroken: true,
        showStable: true,
        showNotExecuted: true,
        showCompilation: true,
        showTests: true,
    });

    if(items.length == 0) {
        httpClient.fetch<ICommitRun[]>(`log/list`)
        .then(data => {
            setItems(data.sort((i,j) => 
                new Date(j.commit.authoredDatetime).getTime() - new Date(i.commit.authoredDatetime).getTime()
            ));
        });
    }

    const toggleFilter = (a) => {
        const prop = a.target.value;
        let newProp: any = {};
        newProp[prop] = !filter[prop];

        setFilter({ ...filter, ...newProp });
    }

    let tmpItems = items
        .filter(i => 
                (filter.showBroken          && i.runs.filter(j => j.isBroken).length > 0)
            ||  (filter.showStable          && i.runs.filter(j => !j.isBroken).length > 0)
            ||  (filter.showNotExecuted     && i.runs.length === 0))

        .filter(i =>
                (filter.showCompilation    && (i.runs.length === 0 || i.runs.filter(j => j.job == "compile").length > 0))
            ||  (filter.showTests          && (i.runs.length === 0 || i.runs.filter(j => j.job == "test").length > 0))
        )
    
    return <>
        <ToggleButtonGroup type="checkbox">
            <ToggleButton onChange={toggleFilter} value="showBroken">hide Broken</ToggleButton>
            <ToggleButton onChange={toggleFilter} value="showStable">hide Stable</ToggleButton>
            <ToggleButton onChange={toggleFilter} value="showNotExecuted">hide NotExecuted</ToggleButton>
            <ToggleButton onChange={toggleFilter} value="showCompilation" variant="info">hide Compilation</ToggleButton>
            <ToggleButton onChange={toggleFilter} value="showTests" variant="info">hide Tests</ToggleButton>
        </ToggleButtonGroup>

        <h2>Showing {tmpItems.length} last commits of {items.length} in 90 days period</h2>
        <Row>
            {tmpItems.map(i => RenderCommitRun(i))}
        </Row>
    </>
}

export class LogComponent extends React.Component<{}, {}, {}> {
    render() {
        return <div>
            <h1>foo</h1>
            {GetLastBuild(null)}
        </div>
    }
}
