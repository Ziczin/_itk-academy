class BaseObjManager {
    constructor(base = {}) {
        this.base = base
        this.container = {}
    }
    add(elem) {
        if (typeof elem === 'object') {
            this.container = Object.assign(this.container, elem)
        }
    }
    get() { return Object.assign(this.container, this.base) }
    view() { let res = new BaseObjManager(this.get()); this.flush(); return res }
    flush() { this.container = {}; return this}
    clear() { this.base = {}; return this }
}

class BaseArrManager {
    constructor(base = []) {
        this.base = base
        this.container = []
    }
    add(elem) {
        this.container = [...this.container, elem]
    }
    get() { return [...this.base, ...this.container] }
    view() { let res = new BaseArrManager(this.get()); this.flush(); return res }
    flush() { this.container = []; return this }
    clear() { this.base = []; return this }
}

class RouteManager extends BaseArrManager {
    build() { return this.get().join('/') + '/'; }
    view() { let res = new RouteManager(this.get()); this.flush(); return res }
}

class QueryManager extends BaseObjManager {
    view() { let res = new QueryManager(this.get()); this.flush(); return res }
    build() {
        const parts = [];
        const enc = encodeURIComponent;
        const src = this.get();

        Object.entries(src).forEach(([key, value]) => {
            let str = value
            if (!(typeof value === 'string')) {
                str = typeof value === 'object' ? JSON.stringify(value) : String(value);
            }
            parts.push(`${enc(key)}=${enc(str)}`);
        });
        return parts.length ? `?${parts.join('&')}` : '';
    }
}

export default class Query {
    constructor(route, query, header, body, onCode) {
        this.route = route;
        this.query = query;
        this.header = header;
        this.body = body;
        this.onCode = onCode;
    }
    
    static new(baseRoute=[], baseQuery={}, baseHeader={}, baseBody={}, baseonCode={}) {
        if (!Array.isArray(baseRoute)) {baseRoute = [baseRoute]}
        return new Query(
            new RouteManager(baseRoute),
            new QueryManager(baseQuery),
            new BaseObjManager(baseHeader),
            new BaseObjManager(baseBody),
            new BaseObjManager(baseonCode),
        );
    }

    view() {
        return new Query(
            this.route.view(),
            this.query.view(),
            this.header.view(),
            this.body.view(),
            this.onCode.view(),
        );
    }

    flush() {
        this.route.flush(),
        this.query.flush(),
        this.header.flush(),
        this.body.flush(),
        this.onCode.flush()
        return this
    }

    at(elem) { this.route.add(elem); return this; }
    via(elem) { this.header.add(elem); return this; }
    with(elem) { this.body.add(elem); return this; }
    where(elem) { this.query.add(elem); return this; }
    on(map) { this.onCode.add(map); return this; }

    get(withStatusCode = false) { return this.fetch('GET', withStatusCode) }
    post(withStatusCode = false) { return this.fetch('POST', withStatusCode) }
    patch(withStatusCode = false) { return this.fetch('PATCH', withStatusCode) }
    delete(withStatusCode = false) { return this.fetch('DELETE', withStatusCode) }
    put(withStatusCode = false) { return this.fetch('PUT', withStatusCode) }

    async fetch(method=null, withStatusCode=false) {
        const route = this.route.build();
        const query = this.query.build();
        const url = route + query;
        const headers = this.header.get();
        const body = this.body.get();
        const onCode = this.onCode.get();

        this.q_url = method + ': ' + url // changed
        this.q_body = body // changed

        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                ...headers,
            }
        };

        if (method !== 'GET') {
            options.body = JSON.stringify(body);
        }

        const response = await fetch(url, options);
        this.flush()

        let data;
        const text = await response.text();
        const parsed = (() => {
            try {
                return text ? JSON.parse(text) : {};
            } catch (err) {
                return null;
            }
        })();
        data = parsed === null ? text : parsed;

        if (Object.prototype.hasOwnProperty.call(onCode, response.status)) {
            onCode[response.status]();
        }
        if (withStatusCode) {
            data = {
                status: response.status,
                data: data,
            };
        }
        return data;
    }

    repeat(delay, method, func) {
        let intervalId = null;

        const schedule = (d) => {
            if (intervalId !== null) clearInterval(intervalId);
            intervalId = setInterval(async () => {
                const res = await this.view().fetch(method);
                if (res.stop) {
                    clearInterval(intervalId);
                    intervalId = null;
                    return;
                }
                if (res.response) {
                    func(res.response);
                    return;
                }
                if (res.delay && typeof res.delay === 'number' && res.delay > 0) {
                    schedule(res.delay);
                }
            }, d);
        };

        schedule(delay);

        return () => {
            if (intervalId !== null) {
                clearInterval(intervalId);
                intervalId = null;
            }
        }
    }
}
