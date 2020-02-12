import 'react-notifications/lib/notifications.css';

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
        
        if(this.onChange) {
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