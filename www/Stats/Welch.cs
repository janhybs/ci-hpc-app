using Accord.Statistics.Testing;
using System;

// https://docs.microsoft.com/en-us/archive/msdn-magazine/2015/november/test-run-the-t-test-using-csharp
namespace CC.Net.Stats
{
    public class Welch
    {

        public double PValue { get; set; }
        public bool Significant { get; set; }
        public double Size { get; set; }
        public double DegreesOfFreedom { get; set; }
        public double EstimatedValue1 { get; set; }
        public double EstimatedValue2 { get; set; }
        public double CriticalValue { get; set; }
        public int N1 { get; set; }
        public int N2 { get; set; }
        public int Radius { get; set; }

        public override string ToString()
        {
            return $"{Significant}([{Radius}] p={PValue:0.00}, df={DegreesOfFreedom:0.00}, cv={CriticalValue:0.00})";
        }

        public static Welch TTest(double[] x, double[] y, int radius)
        {
            var ttest = new TwoSampleTTest(x, y);
            ttest.Size = 0.01;
            return new Welch
            {
                N1 = x.Length,
                N2 = y.Length,
                Radius = radius,
                PValue = ttest.PValue,
                Significant = ttest.Significant,
                Size = ttest.Size,
                DegreesOfFreedom = ttest.DegreesOfFreedom,
                EstimatedValue1 = ttest.EstimatedValue1,
                EstimatedValue2 = ttest.EstimatedValue2,
                CriticalValue = ttest.CriticalValue,
            };

            /*double sumX = 0.0;
            double sumY = 0.0;
            for (int i = 0; i < x.Length; ++i)
            {
                sumX += x[i];
            }
            for (int i = 0; i < y.Length; ++i)
            {
                sumY += y[i];
            }

            int n1 = x.Length;
            int n2 = y.Length;
            double meanX = sumX / n1;
            double meanY = sumY / n2;

            double sumXminusMeanSquared = 0.0; // Calculate variances
            double sumYminusMeanSquared = 0.0;
            for (int i = 0; i < n1; ++i)
            {
                sumXminusMeanSquared += (x[i] - meanX) * (x[i] - meanX);
            }
            for (int i = 0; i < n2; ++i)
            {
                sumYminusMeanSquared += (y[i] - meanY) * (y[i] - meanY);
            }
            double varX = sumXminusMeanSquared / (n1 - 1);
            double varY = sumYminusMeanSquared / (n2 - 1);

            double top = (meanX - meanY);
            double bot = Math.Sqrt((varX / n1) + (varY / n2));
            double t = top / bot;

            double num = ((varX / n1) + (varY / n2)) * ((varX / n1) + (varY / n2));
            double denomLeft = ((varX / n1) * (varX / n1)) / (n1 - 1);
            double denomRight = ((varY / n2) * (varY / n2)) / (n2 - 1);
            double denom = denomLeft + denomRight;
            double df = num / denom;
            double p = Student(t, df);

            return new Welch {
                Pval = p,
                DF = df,
                MeanX = meanX,
                MeanY = meanY,
            };*/
        }
        /*public static double Student(double t, double df)
        {
            // for large integer df or double df
            // adapted from ACM algorithm 395
            // returns 2-tail p-value
            double n = df; // to sync with ACM parameter name
            double a, b, y;
            t = t * t;
            y = t / n;
            b = y + 1.0;
            if (y > 1.0E-6) y = Math.Log(b);
            a = n - 0.5;
            b = 48.0 * a * a;
            y = a * y;
            y = (((((-0.4 * y - 3.3) * y - 24.0) * y - 85.5) /
              (0.8 * y * y + 100.0 + b) + y + 3.0) / b + 1.0) *
              Math.Sqrt(y);
            return 2.0 * Gauss(-y); // ACM algorithm 209
        }

        public static double Gauss(double z)
        {
            // input = z-value (-inf to +inf)
            // output = p under Standard Normal curve from -inf to z
            // e.g., if z = 0.0, function returns 0.5000
            // ACM Algorithm #209
            double y; // 209 scratch variable
            double p; // result. called 'z' in 209
            double w; // 209 scratch variable
            if (z == 0.0)
                p = 0.0;
            else
            {
                y = Math.Abs(z) / 2;
                if (y >= 3.0)
                {
                    p = 1.0;
                }
                else if (y < 1.0)
                {
                    w = y * y;
                    p = ((((((((0.000124818987 * w
                      - 0.001075204047) * w + 0.005198775019) * w
                      - 0.019198292004) * w + 0.059054035642) * w
                      - 0.151968751364) * w + 0.319152932694) * w
                      - 0.531923007300) * w + 0.797884560593) * y * 2.0;
                }
                else
                {
                    y = y - 2.0;
                    p = (((((((((((((-0.000045255659 * y
                      + 0.000152529290) * y - 0.000019538132) * y
                      - 0.000676904986) * y + 0.001390604284) * y
                      - 0.000794620820) * y - 0.002034254874) * y
                      + 0.006549791214) * y - 0.010557625006) * y
                      + 0.011630447319) * y - 0.009279453341) * y
                      + 0.005353579108) * y - 0.002141268741) * y
                      + 0.000535310849) * y + 0.999936657524;
                }
            }
            if (z > 0.0)
                return (p + 1.0) / 2;
            else
                return (1.0 - p) / 2;
        }*/
    }
}