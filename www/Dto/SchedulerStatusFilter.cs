using CC.Net.Collections;

namespace CC.Net.Dto
{

    public class SchedulerFilter
    {
        public ColSchedulerStatus status { get; set; } = ColSchedulerStatus.Processed;
        public int limit { get; set; } = 10;
    }
}