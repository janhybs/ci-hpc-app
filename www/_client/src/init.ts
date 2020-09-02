import { IIndexInfo, ICommitBaseline } from "./models/DataModel";

interface HttpClientConfig {
    baseUrl: string;
    headers: { [key: string]: string };
}

class HttpClient {
    constructor(private config: HttpClientConfig) {
    }

    public fetch<T>(url: string, data: any = null, method: string = "auto"): Promise<T> {
        const headers = this.config.headers || {};
        const body = data === null ? null : JSON.stringify(data);
        method = method === "auto" ? (data === null ? "get" : "post") : method;
        return new Promise((resolve, reject) => {
            fetch(`${this.config.baseUrl}${url}`, { method, headers, body })
                .then(result => result.json())
                .catch(reason => reject(reason))
                .then(data => resolve(data))
                .catch(reason => reject(reason))
        });
    }
}

export class LayoutUtils {
    public onChange?: (style: string) => void;

    public className: string = "";
    public setContainerStyle(style: string) {
        this.className = style

        if (this.onChange) {
            this.onChange(this.className);
        }
    }
}

export const httpClient = new HttpClient({
    baseUrl: 'api/',
    headers: {
        'Content-Type': 'application/json'
    },
});

export const layoutUtils = new LayoutUtils();


const cfg = (test, benchmark, mesh, cpus = 1): IIndexInfo => {
    return {
        project: "flow123d",
        test, benchmark, mesh,
    } as IIndexInfo;
}


export const configurations: IIndexInfo[] = [
    ...['1_15662_el', '2_31498_el'].map(mesh =>
        cfg(
            "01_square_regular_grid",
            "transport.yaml",
            mesh
        ),
    ),
    ...['flow_bddc.yaml', 'flow_dg.yaml', 'flow_fv.yaml'].map(benchmark =>
        cfg(
            "02_cube_123d",
            benchmark,
            "1_15786_el"
        ),
    ),
    ...['flow_bddc.yaml', 'flow_dg.yaml', 'flow_fv.yaml'].map(benchmark =>
        cfg(
            "02_cube_123d",
            benchmark,
            "2_29365_el"
        ),
    ),
] as IIndexInfo[];


export const baselines: ICommitBaseline[] = [
    { commit: "4db4b481073edc73c22031aeb86c31c9b633025a", name: "v3.0.4" },
    { commit: "f72c4b41f40db374168cc91ca59e6e7d87555596", name: "v3.0.2" },
    { commit: "b04af7fb08d423036b30ea00c3b8941b0c91e3c0", name: "v2.2.1" },
    { commit: "6b54fcf046d36cb37bfcc53bd6e613eca1459bda", name: "v3.0.0" },
];