from __future__ import annotations

from flask import Blueprint, current_app, flash, g, redirect, render_template, request, url_for

from echo_app.blog.forms import PostForm
from echo_app.blog.services import (
    create_post as create_post_record,
    delete_post as delete_post_record,
    get_post,
    list_posts,
    posts_by_tag as lookup_posts_by_tag,
    record_post_interaction,
    search_posts,
    tag_cloud,
    update_post,
    user_posts,
    weekly_digest as build_weekly_digest,
)
from echo_app.utils.auth import login_required


blog_bp = Blueprint("blog", __name__)


def _pagination_context(pagination):
    return {
        "posts": pagination.items,
        "page": pagination.page,
        "total_pages": pagination.pages,
        "has_prev": pagination.has_prev,
        "has_next": pagination.has_next,
    }


@blog_bp.get("/")
def index():
    page = request.args.get("page", 1, type=int)
    pagination = list_posts(page=page, per_page=current_app.config["POSTS_PER_PAGE"])
    context = _pagination_context(pagination)
    context["tag_cloud"] = tag_cloud()
    return render_template("blog/index.html", **context)


@blog_bp.get("/post/<int:post_id>")
def view_post(post_id: int):
    post = get_post(post_id)
    if post is None:
        flash("Post not found.", "error")
        return redirect(url_for("blog.index"))
    record_post_interaction(post)
    return render_template("blog/post.html", post=post, versions=post.versions)


@blog_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        post = create_post_record(author=g.current_user, title=form.title.data, content=form.content.data, tags_raw=form.tags.data)
        flash("Post created successfully.", "success")
        return redirect(url_for("blog.view_post", post_id=post.id))
    return render_template("blog/create.html", form=form)


@blog_bp.route("/edit/<int:post_id>", methods=["GET", "POST"])
@login_required
def edit_post(post_id: int):
    post = get_post(post_id)
    if post is None:
        flash("Post not found.", "error")
        return redirect(url_for("blog.index"))
    if post.user_id != g.current_user.id:
        flash("You can only edit your own posts.", "error")
        return redirect(url_for("blog.index"))

    form = PostForm()
    if form.validate_on_submit():
        update_post(post=post, title=form.title.data, content=form.content.data, tags_raw=form.tags.data)
        flash("Post updated successfully.", "success")
        return redirect(url_for("blog.view_post", post_id=post.id))
    if request.method == "GET":
        form.title.data = post.title
        form.content.data = post.content
        form.tags.data = ", ".join(post.tag_list)
    return render_template("blog/edit.html", form=form, post=post)


@blog_bp.post("/delete/<int:post_id>")
@login_required
def delete_post(post_id: int):
    post = get_post(post_id)
    if post is None:
        flash("Post not found.", "error")
        return redirect(url_for("blog.index"))
    if post.user_id != g.current_user.id:
        flash("You can only delete your own posts.", "error")
        return redirect(url_for("blog.index"))

    delete_post_record(post)
    flash("Post deleted successfully.", "success")
    return redirect(url_for("blog.index"))


@blog_bp.get("/search")
def search():
    query = request.args.get("query", "").strip()
    posts = search_posts(query) if query else []
    return render_template("blog/search.html", posts=posts, query=query)


@blog_bp.get("/tags/<slug>")
def posts_by_tag(slug: str):
    tag, posts = lookup_posts_by_tag(slug)
    if tag is None:
        flash("Tag not found.", "error")
        return redirect(url_for("blog.index"))
    return render_template("blog/tag.html", posts=posts, tag=tag)


@blog_bp.get("/digest")
def weekly_digest():
    return render_template("blog/digest.html", weekly_digest=build_weekly_digest())


@blog_bp.get("/my-posts")
@login_required
def my_posts():
    return render_template("blog/my_posts.html", posts=user_posts(g.current_user))
