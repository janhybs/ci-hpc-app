
	export const enum ColSchedulerStatus {
		NotProcessed = 10,
		Running = 20,
		Processed = 30
	}
	export interface IColIndexInfoRun {
		duration: number;
		isBroken: boolean;
		job: string;
		returncode: number;
	}
	export interface IColRepoInfo {
		author: string;
		authoredDatetime: Date;
		branch: string;
		branches: string[];
		children: string[];
		commit: string;
		committedDatetime: Date;
		distance: number;
		durations: number[];
		email: string;
		id: IObjectId;
		message: string;
		objectId: string;
		parents: string[];
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
		info: IColRepoInfo;
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
	export interface ICommitRun {
		commit: IColRepoInfo;
		runs: IColIndexInfoRun[];
	}
	export interface IDurInfo {
		avg: number;
		max: number;
		min: number;
		n: number;
	}
	export interface IDurInfoWrapper {
		commit: string;
		duration: IDurInfo;
		frame: string;
		path: string;
	}
	export interface IIndexInfo {
		benchmark: string;
		branch: string;
		commit: string;
		commitShort: string;
		cpus: any;
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
		commitInfo: IColRepoInfo;
		count: number;
		durations: number[];
		info: IGitInfo;
		isBroken: boolean;
		left: string[];
		right: string[];
		welch: IWelch;
		welchType: WelchType;
	}
	export interface ISimpleTimersEx extends ISimpleTimers {
		high: number;
		low: number;
		median: number;
		q1: number;
		q3: number;
	}
	export interface IGitInfo {
		branch: string;
		branches: string[];
		date: Date;
		message: string;
	}
	export const enum WelchType {
		Improvement = 1,
		Decline = 2,
		Unknown = 3
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
		statistic: number;
	}
	export interface IBaseline {
		commit: string;
		title: string;
	}
	export interface ICommitBaseline {
		name: string;
		value: string;
	}
	export interface ICompareCommitDto {
		commitA: IDurInfoWrapper[];
		commitB: IDurInfoWrapper[];
		rootA: IDurInfoWrapper;
		rootB: IDurInfoWrapper;
	}
	export interface ICompareCommitFilter {
		commitA: string;
		commitB: string;
		commits: string[];
		frame: string;
		info: IIndexInfo;
	}
	export interface ICompareCommitFlatDto {
		items: IDurInfoWrapper[];
	}
	export interface IConfigurationDto {
		benchmarkList: IIndexInfo[];
		branches: IColRepoInfo[];
		branchNames: string[];
		frontendConfig: IFrontendConfig;
	}
	export interface IFrontendConfig {
		baselines: IBaseline[];
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
