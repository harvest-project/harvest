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
    static pageRoutesComponents = [];

    static registerPageRoutesComponent(component) {
        pushUnique(this.pageRoutesComponents, component);
    }
}

export class MenuRegistry {
    static mainMenuItems = [];
    static settingsMenuItems = [];

    static registerMainMenuItem(menuItem) {
        pushUnique(this.mainMenuItems, menuItem);
    }

    static registerSettingsMenuItem(menuItem) {
        pushUnique(this.settingsMenuItems, menuItem);
    }
}
