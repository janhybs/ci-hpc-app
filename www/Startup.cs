using CC.Net.Config;
using CC.Net.Db;
using CC.Net.Services;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.SpaServices.ReactDevelopmentServer;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using System;

namespace CC.Net
{
    public class Startup
    {
        public Startup(IConfiguration configuration)
        {
            Console.WriteLine("Starting application");
            Configuration = configuration;
            MongoDBConfig = Configuration.GetSection("MongoDB").Get<MongoDBConfig>();
            AppOptions = Configuration.Get<AppOptions>();
        }

        public IConfiguration Configuration { get; set; }
        public MongoDBConfig MongoDBConfig { get; set; }
        public AppOptions AppOptions { get; set; }

        // This method gets called by the runtime. Use this method to add services to the container.
        public void ConfigureServices(IServiceCollection services)
        {
            services.AddOptions();
            services.AddSingleton(MongoDBConfig);
            services.AddSingleton(AppOptions);
            services.AddSingleton(new GitInfoService(AppOptions));
            services.AddSingleton<DbService>();
            services.AddSingleton<RepoInfoCache>();
            services.AddControllersWithViews();

            // In production, the React files will be served from this directory
            services.AddSpaStaticFiles(configuration =>
            {
                configuration.RootPath = "_client/build";
            });
        }

        public void Configure(IApplicationBuilder app, IWebHostEnvironment env, IServiceProvider serviceProvider)
        {
            if (env.IsDevelopment())
            {
                app.UseDeveloperExceptionPage();
            }
            else
            {
                app.UseExceptionHandler("/Error");
                // 30 days, see https://aka.ms/aspnetcore-hsts.
                app.UseHsts();
            }

            var db = serviceProvider.GetService<DbService>();

            app.UseHttpsRedirection();
            app.UseStaticFiles();
            app.UseSpaStaticFiles();

            app.UseRouting();

            app.UseEndpoints(endpoints =>
            {
                endpoints.MapControllerRoute(
                    name: "default",
                    pattern: "{controller}/{action=Index}/{id?}");
            });

            app.UseSpa(spa =>
            {
                spa.Options.SourcePath = "_client";

                if (env.IsDevelopment())
                {
                    spa.UseReactDevelopmentServer(npmScript: "start");
                }
            });
        }
    }
}
