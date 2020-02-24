import { store } from 'react-notifications-component';

export class NotificationApi{
    static success(message: string, title: string = "", duration: number = 300) {
        store.addNotification({
            message: message,
            title: title,
            type: "success",
            container: "top-right",
            animationIn: ['animated', 'faster', 'fadeIn'],
            animationOut: ['animated', 'faster', 'fadeOut'],
            slidingEnter: {
                duration: 100,
                timingFunction: "ease-out"
            },
            slidingExit: {
                duration: 100,
                timingFunction: "ease-out"
            },
            dismiss: {
                duration: duration,
                pauseOnHover: true
            }
        });
    }
}