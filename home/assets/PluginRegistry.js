function pushUnique(arr, item) {
    if (arr.indexOf(item) !== -1) {
        throw 'Item already registered.';
    }
    arr.push(item);
}

export class TrackerRegistry {
    static trackers = [];
    static trackersByName = {};

    static register(tracker) {
        pushUnique(this.trackers, tracker);
        this.trackersByName[tracker.trackerName] = tracker;
    }
}

export class RouteRegistry {
    static pageRoutes = [];
    static fullPageRoutes = [];
    static fullScreenRoutes = [];

    static addPageRoute(route) {
        pushUnique(this.pageRoutes, route);
    }

    static addFullPageRoute(route) {
        pushUnique(this.fullPageRoutes, route);
    }

    static addFullScreenRoute(route) {
        pushUnique(this.fullScreenRoutes, route);
    }
}

export class MenuRegistry {
    static mainMenuItems = [];
    static settingsMenuItems = [];

    static addMainMenuItem(menuItem) {
        pushUnique(this.mainMenuItems, menuItem);
    }

    static addSettingsMenuItem(menuItem) {
        pushUnique(this.settingsMenuItems, menuItem);
    }
}
