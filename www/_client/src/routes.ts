
import { Home } from './components/Home';
import { SchedulerList } from './routes/SchedulerList';
import { BenchmarkView } from './routes/BenchmarkView';

export interface IRoute {
    title: string;
    href: string;
    component: any;
    path?: any;
}

export const routes: IRoute[] = [
    { title: "Home", href: "/", component: Home },
    { title: "Scheduler", href: "/scheduler", component: SchedulerList },
    { title: "Benchmarks", href: "/benchmarks/0", component: BenchmarkView, path: "/benchmarks/:index" },
];