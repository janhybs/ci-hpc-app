
import { Home } from './components/Home';
import { SchedulerList } from './routes/SchedulerList';
import { BenchmarkView } from './routes/BenchmarkView';

export interface IRoute {
    title: string;
    href: string;
    component: any;
}

export const routes = [
    { title: "Home", href: "/", component: Home },
    { title: "Scheduler", href: "/scheduler", component: SchedulerList },
    { title: "Benchmarks", href: "/benchmarks", component: BenchmarkView },
];