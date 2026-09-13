package com.sample.cms.embedded.service;

import okhttp3.OkHttpClient;

import java.util.concurrent.TimeUnit;

public class HttpClientFactory {
    /**
     * Builds a new {@link OkHttpClient} configured with connect and read timeouts suitable for
     * LLM generation calls, which may run longer than typical HTTP requests due to model thinking time.
     *
     * @return A newly configured {@link OkHttpClient} instance.
     */
    public static OkHttpClient newInstance() {
        return new OkHttpClient.Builder()
                .connectTimeout(10, TimeUnit.SECONDS)
                .readTimeout(90, TimeUnit.SECONDS)
                .build();
    }
}
