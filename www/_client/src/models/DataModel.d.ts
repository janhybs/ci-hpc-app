
	export const enum ColSchedulerStatus {
		NotProcessed = 10,
		Running = 20,
		Processed = 30
	}
	export interface IColScheduler {
		details: IColSchedulerDetails;
		id: IObjectId;
		index: IIndexInfo;
		objectId: string;
		status: ColSchedulerStatus;
		worker: string;
	}
	export interface IColSchedulerDetails {
		priority: number;
		repetitions: number;
	}
	export interface IColTimers {
		id: IObjectId;
		index: IIndexInfo;
		objectId: string;
		result: IColTimersResult;
	}
	export interface IColTimersResult {
		cntAlloc: number;
		cntDealloc: number;
		duration: number;
		durRatio: number;
		executed: number;
		fileLine: number;
		filePath: string;
		function: string;
		memAlloc: number;
		memDealloc: number;
		name: string;
		path: string;
	}
	export interface IObjectId {
		creationTime: Date;
		empty: IObjectId;
		increment: number;
		machine: number;
		pid: number;
		timestamp: number;
	}
	export interface IIndexInfo {
		benchmark: string;
		branch: string;
		commit: string;
		commitShort: string;
		frame: string;
		host: any;
		job: string;
		mesh: string;
		project: string;
		test: string;
		uuid: any;
	}
	export interface ISimpleTimer {
		branch: string;
		commit: string;
		duration: number;
		objectId: string;
	}
	export interface ISimpleTimers {
		branch: string;
		commit: string;
		count: number;
		durations: number[];
		high: number;
		info: IGitInfo;
		isBroken: boolean;
		low: number;
		median: number;
		q1: number;
		q3: number;
		welch: IWelch;
	}
	export interface IGitInfo {
		branch: string;
		branches: string[];
		date: Date;
		message: string;
	}
	export interface IWelch {
		criticalValue: number;
		degreesOfFreedom: number;
		estimatedValue1: number;
		estimatedValue2: number;
		n1: number;
		n2: number;
		pValue: number;
		radius: number;
		significant: boolean;
		size: number;
	}
	export interface ISchedulerFilter {
		limit: number;
		status: ColSchedulerStatus;
	}
	export interface ITimersFilter {
		days: number;
		info: IIndexInfo;
		limit: number;
	}
