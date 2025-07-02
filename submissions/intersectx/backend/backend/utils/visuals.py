if __name__ == "__main__":
    from cloudinary.utils import cloudinary_url

    url, options = cloudinary_url(
        public_id="v1748028864/3395b47a-10f2-445e-9ecb-694aecc5d982.html",  # must include .html
        resource_type="raw",
        type="upload",
        attachment=False,  # 🔑 this makes it viewable, not downloadable
        sign_url=True,  # 🔐 required for advanced features
    )

    print("Embed in iframe:")
    print(f'<iframe src="{url}" width="800" height="600" frameborder="0"></iframe>')
