import React from "react";

import { observable } from "mobx";
import { ISimpleTimers, IIndexInfo, ITimersFilter, ISimpleTimersEx } from "../models/DataModel";
import { configurations } from "../init";


export class BenchmarkViewModel {

    @observable
    public configuration: IIndexInfo = configurations[0] as IIndexInfo;

    public items: ISimpleTimersEx[] = [];

    public ratio: number = NaN;

    public get filter(): ITimersFilter {
        return {
            info: this.configuration,
            limit: 5000,
        } as ITimersFilter;
    }
}
export const getConfigurationName = (item: IIndexInfo) =>{
    return `${item.test} ${item.benchmark} ${item.mesh}`;
}

export const getColor = (point: ISimpleTimers, commitId="") => {
    if(point.welch == null)
    {
        return "gray";
    }
    return point.isBroken
        ? "gray"
        : (point.welch !== null && point.welch.significant
            ? (point.welch.estimatedValue1 < point.welch.estimatedValue2
                ? (point?.commit === commitId ? "darkgreen" : "green")
                : (point?.commit === commitId ? "darkred" : "red")
                )
            : null);
}

export const trimSha = (prev: string, current: string) => {
    return (prev + ", " + current).split(", ").map(i => i.substr(0, 5)).join(", ");
}