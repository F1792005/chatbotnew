if __name__ == "__main__":
    import uvicorn

    # Run the FastAPI app in chat_router
    uvicorn.run("chat_router:app", host="0.0.0.0", port=8000, reload=True)
